"""Script to perform measurements for the characterization of nanoionic devices."""

import time

import pandas as pd

from SimpleKeithley236.Keithley236 import Keithley236


def read_set_times(file):
    """Returns the first column of an Excel file as list."""

    df = pd.read_excel(file, header=None)  # pylint: disable=C0103
    df.iloc[:, 0] = df.iloc[:, 0] * 0.1
    return df.iloc[:, 0].tolist()


def measurement(file_set_times, **kwargs):
    """
    Performs measurements for the characterization of nanoionic memories using
    a Keihtley 236.

    Parameters
    ----------
    :param file_set_times: str
        The file location of an Excel file containing the individual set times.
    :key gpib_address: int
        GPIB adress of the Keihtley 236. (Default is 16).
    :key compliance: str
        Compliance Value [A]. Scientific notation required e.g "1E-9" for 1nA.
        (Default value is 1E-9).
    :key measurement_delay: float
        Delay time [s] between applying the measuring voltage and the start of the measurement.
        (Default value is 30).
    :key measurement_range: str
        Measurement source_range for the current. Allowed values are: Auto, 1nA, 10nA, 100nA,
        1µA, 10µA, 100µA, 1mA, 10mA and 100mA. (Default value is 1nA).
    :key measurement_voltage: float
        Applied voltage [V] during the measurement step. (Default value is 1).
    :key rest_period: float
        Delay time [s] between the end of the measurement and the start of the next set pulse.
        (Default value is 120).
    :key set_voltage: float
        Applied voltage [V] during the set step. (Default value is 1).
    """

    set_times = read_set_times(file_set_times)

    smu = Keithley236(kwargs.get('gpib_address', 16),
                      kwargs.get('compliance', '1E-9'),
                      kwargs.get('measurement_range', '1nA'))

    smu.measurement(kwargs.get('measurement_voltage', 0.1),
                    kwargs.get('measurement_delay', 30))

    for set_time in set_times:
        smu.impulse(kwargs.get('set_voltage', 1), set_time)
        smu.measurement(kwargs.get('measurement_voltage', 0.1),
                        kwargs.get('measurement_delay', 30))
        time.sleep(kwargs.get('rest_period', 120))


if __name__ == '__main__':

    keyword_arguments = {"set_voltage": 1.0,
                         "measurement_voltage": 0.1,
                         "measurement_delay": 6,
                         "rest_period": 30,
                         "gpib_address": 16,
                         "measurement_range": "1mA",
                         "compliance": "1E-3",
                         }

    measurement(file_set_times='set_zeit_log.xls', **keyword_arguments)
