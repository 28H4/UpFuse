"""Script to perform periodic measurements with constant applied voltage."""
import datetime
import time

import pandas as pd

from SimpleKeithley236.Keithley236 import Keithley236
from measurement import store_data


def single_measurement(smu, output_file, start_time):
    """
    Trigges a single measurement and appends the result (passed time,
    measurement result) to the specified file.
    """
    current = smu._query_("H0").rstrip()
    store_data(output_file, {time.time() - start_time: current})


def interval_measurement(n, period, measurement_args, measurement_delay=1.10):
    """
    Performs n measurements at intervals of period.
    The measurement results are append to the output_file (passed time, measurement).

    :param n: int
        Number of measurements.
    :param period: float
        Time interval between measurements [s].
    :param measurement_args: iterable
        List of smu, output_file and start_time which will be passed to
        single_measurement().
    :key measurement_delay: float, optional, default=1.10
        The measurement is triggered at a time interval of "measurement_delay"
        before the end of the measurement period to compensate for the duration
        of the measurements.
    """

    performed_runs = 0

    while performed_runs < n:
        start_time_interval = time.time()
        time.sleep(period - measurement_delay)
        single_measurement(*measurement_args)
        try:
            time.sleep(time.time() - start_time_interval - period)
        except ValueError:
            pass

        performed_runs += 1


def continuous_measurement(input_file, results_file, **kwargs):
    """
    Starts an event loop after the delay, which performs n-measurements at
    intervals of t and appends the measurement data (time since the beginning
    of the delay, current intensity measurement value) to the file.

    :param input_file: str
        File path of an Excel file from whose first worksheet the pattern of
        the measurement (voltage, period duration, repetitions) is to be read.
    :param results_file: str
        File path for the output file e.g. "output_files/test.csv".
    :key gpib_address: int
        GPIB adress of the Keihtley 236. (Default is 16).
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

    smu._set_trigger_(True)
    smu._set_output_data_format_("source and measure value")

    measurement_settings = pd.read_excel(input_file,
                                         header=0,
                                         names=('voltage', 'time_interval', 'repeatings'),
                                         usecols="A:C").dropna()  # pylint: disable=C0103

    start_time = time.time()
    smu._set_operate_(True)
    for index, row in measurement_settings.iterrows():
        smu._set_bias_(row.voltage)
        interval_measurement(row.repeatings, row.time_interval, (smu, results_file, start_time))

    timestamp_now = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
    store_data(results_file, {"completion time": timestamp_now})


if __name__ == '__main__':
    keyword_arguments = {
        "range": "Auto",
        "compliance": None,
        # "gpib_address": 16,
    }

    continuous_measurement(r'input_files/input_continuous_measurement.xlsx',
                           r"output_files/test.csv",
                           **keyword_arguments)
