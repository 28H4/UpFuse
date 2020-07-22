"""Script to perform measurements for the characterization of nanoionic devices."""
import datetime
import time

import pandas as pd


from SimpleKeithley236.Keithley236 import Keithley236


def read_set_times(file):
    """Returns the first column of an Excel file as list."""

    df = pd.read_excel(file, header=None)  # pylint: disable=C0103
    df.iloc[:, 0] = df.iloc[:, 0]
    return df.iloc[:, 0].tolist()


def store_data(file, data):
    """
    Appends dict to csv-file. Attached lines consist of "key,value".
    :param file: str
        Path t output file.
    :param data: dict
        dict to be saved.
    """
    with open(file, "a", encoding='utf-8') as myfile:
        for key, value in data.items():
            myfile.write(f"{key},{value}\n")


def measurement(file_set_times, output_file, **kwargs):
    """
    Performs measurements for the characterization of nanoionic memories using
    a Keihtley 236.

    Parameters
    ----------
    :param file_set_times: str
        The file location of an Excel file containing the individual set times.
    :param output_file: str
        File paths of the output file (settings and measurement data are attached).
    :key gpib_address: int
        GPIB adress of the Keihtley 236. (Default is 16).
    :key measurement_delay: float
        Delay time [s] between applying the measuring voltage and the start of
        the measurement. (Default value is 30).
    :key measurement_compliance: str
        Compliance Value [A]. Scientific notation required e.g "1E-9" for 1nA.
        (Default value is 1E-8).
    :key measurement_range: str
        Measurement range during the measurement step. Allowed values are: Auto,
         1nA, 10nA, 100nA, 1µA, 10µA, 100µA, 1mA, 10mA and 100mA. (Default value is 10nA).
    :key measurement_voltage: float
        Applied voltage [V] during the measurement step. (Default value is 1).
    :key rest_period: float
        Delay time [s] between the end of the measurement and the start of the
        next set pulse. (Default value is 120).
    :key set_voltage: float
        Applied voltage [V] during the set step. (Default value is 1).
    :key set_compliance: str
        Compliance Value [A] during the set step. Scientific notation required
        e.g "1E-9" for 1nA. (Default value is 1E-5).
    :key set_range: str
        Measurement range during the set step. Allowed values are: Auto, 1nA,
        10nA, 100nA, 1µA, 10µA, 100µA, 1mA, 10mA and 100mA. (Default value is 10µA).
    """

    timestamp_now = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
    store_data(output_file, {"start time": timestamp_now})
    store_data(output_file, kwargs)

    set_times = read_set_times(file_set_times)

    smu = Keithley236(kwargs.get('gpib_address', 16))

    current = smu.measurement(kwargs.get('measurement_voltage', 0.1),
                              kwargs.get('measurement_compliance', "1E-8"),
                              kwargs.get('measurement_range', "10nA"),
                              kwargs.get('measurement_delay', 30),)

    store_data(output_file, {"0": current})

    for set_time in set_times:
        smu.impulse(kwargs.get('set_voltage', 1),
                    set_time,
                    kwargs.get('set_compliance', "1E-5"),
                    kwargs.get('set_range', "10µA"))
        current = smu.measurement(kwargs.get('measurement_voltage', 0.1),
                                  kwargs.get('measurement_compliance', "1E-8"),
                                  kwargs.get('measurement_range', "10nA"),
                                  kwargs.get('measurement_delay', 30))
        store_data(output_file, {set_time: current})
        time.sleep(kwargs.get('rest_period', 120))

    timestamp_now = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
    store_data(output_file, {"start time": timestamp_now})


if __name__ == '__main__':

    keyword_arguments = {"set_voltage": 1.0,
                         "measurement_voltage": 0.1,
                         "measurement_delay": 6,
                         "rest_period": 30,
                         # "gpib_address": 16,
                         "measurement_range": "10nA",
                         "measurement_compliance": "1E-8",
                         "set_range": "10µA",
                         "set_compliance": "1E-5",
                         }

    measurement(r'input_files/set_zeit_log.xls',
                r"output_files/test.csv",
                **keyword_arguments)
