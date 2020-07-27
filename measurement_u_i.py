"""Script to perform periodic measurements with constant applied voltage."""
import datetime
import threading
import time

from twisted.internet import task, reactor

from SimpleKeithley236.Keithley236 import Keithley236
from measurement import store_data


class LoopingCallWithCounter:
    """Wrapper class to count the event loops and stop the loop after n repetitions."""
    def __init__(self, count, f, *args):
        self.i = 0
        def wrapper():
            if self.i >= count:
                self.lc.stop()
                reactor.stop()
            else:
                f(*args)
                self.i += 1
        self.lc = task.LoopingCall(wrapper)


def single_measurement(smu, file, start_time):
    """
    Trigges a single measurement and appends the result (passed time,
    measurement result) to the specified file.
    """
    current = smu._query_("H0").rstrip()
    store_data(file, {time.time() - start_time: current})


def interval_measurement(n, t, *measurement_args):
    """
    Starts an event loop which periodically triggers a measurement.
    The measurement results are append to the file (passed time, measurement).
    """
    LoopingCallWithCounter(n, single_measurement, *measurement_args).lc.start(t)


def continuous_measurement(results_file, **kwargs):
    """
    Starts an event loop after the delay, which performs n-measurements at
    intervals of t and appends the measurement data (time since the beginning
    of the delay, current intensity measurement value) to the file.
    :param results_file:
    :key gpib_address: int
        GPIB adress of the Keihtley 236. (Default is 16).
    :key n_measurements:int
        Number of measurements which will be performed. (Default is 10)
    :key time_interval: float
        Period of the measurements [s]. (Default is 2).
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

    timestamp_now = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
    store_data(results_file, {"start time": timestamp_now})
    store_data(results_file, kwargs)

    smu = Keithley236(kwargs.get('gpib_address', 16),
                      kwargs.get('compliance', "1E-10"),
                      kwargs.get('range', "1nA"),
                      )

    smu._set_bias_(kwargs.get('voltage', 0.01))
    smu._set_trigger_(True)
    smu._set_output_data_format_("measure value")
    smu._set_operate_(True)
    start_time = time.time()
    time.sleep(kwargs.get("delay", 1))

    reactor.callWhenRunning(interval_measurement,
                            *(kwargs.get("n_measurements", 5), kwargs.get("time_interval", 2)),
                            *(smu, results_file, start_time))
    reactor.run()

    timestamp_now = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
    store_data(results_file, {"completion time": timestamp_now})


if __name__ == '__main__':
    keyword_arguments = {"voltage": 0.1,
                         "range": "Auto",
                         "compliance": None,
                         "n_measurements": 5,
                         "time_interval": 2,
                         "delay": 5,
                         # "gpib_address": 16,
                         }

    continuous_measurement(r"output_files/test.csv", **keyword_arguments)
