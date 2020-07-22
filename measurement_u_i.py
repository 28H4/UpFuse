"""Script to perform periodic measurements with constant applied voltage."""

import threading
import time

from twisted.internet import task, reactor

from SimpleKeithley236.Keithley236 import Keithley236
from measurement import store_data


def single_measurement(smu, file, start_time):
    """
    Trigges a single measurement and appends the result (passed time,
    measurement result) to the specified file.
    """

    current = smu._query_("H0").rstrip()
    store_data(file, {time.time() - start_time: current})


def interval_measurement(smu, file, start_time, time_interval):
    """
    Starts an event loop which periodically triggers a measurement.
    The measurement results are append to the file (passed time, measurement).
    """

    loop = task.LoopingCall(single_measurement, *(smu, file, start_time))
    loop.start(time_interval)
    reactor.run(installSignalHandlers=0)


def continuous_measurement(file, **kwargs):
    """

    :param file:
    :key n_measurements:int
        Number of measurements which will be performed. (Default is 10)
    :key time_interval: float
        Period of the measurements [s]. (Default is 2). A to small value will
        result in a trigger overrun.
    :key measurement_voltage: float
        Applied voltage [V]. (Default value is 0.01).
    :key compliance: str
        Compliance Value [A]. Scientific notation required
        e.g "1E-9" for 1nA. (Default value is 1E-10).
    :key set_range: str
        Measurement range. Allowed values are: Auto, 1nA,
        10nA, 100nA, 1µA, 10µA, 100µA, 1mA, 10mA and 100mA.
        (Default value is 1nA).
    """
    smu = Keithley236(kwargs.get('gpib_address', 16),
                      kwargs.get('compliance', "1E-10"),
                      kwargs.get('range', "1nA"),
                      )

    smu._set_bias_(kwargs.get('voltage', 0.01))
    smu._write_("T1,4,4,0")
    smu._set_trigger_(True)
    smu._set_output_data_format_("measure value")
    smu._set_operate_(True)

    measurement_thread = threading.Thread(target=interval_measurement,
                                          args=(smu, file, time.time(),
                                                kwargs.get("time_interval", 2))
                                          )
    measurement_thread.start()

    duration = kwargs.get('n_measurements', 10)*kwargs.get('time_interval', 2)
    end_timestamp = time.time() + duration
    while time.time() < end_timestamp:
        time.sleep(1)

    reactor.stop()


if __name__ == '__main__':
    keyword_arguments = {"voltage": 0.1,
                         "range": "100nA",
                         "compliance": "5E-8",
                         "n_measurements": 10,
                         "time_interval": 2,
                         # "gpib_address": 16,
                         }

    continuous_measurement(r"output_files/test.csv", **keyword_arguments)
