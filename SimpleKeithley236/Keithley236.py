import time
import re
import math

import pyvisa


class Keithley236:
    """
    Minimal control interface (GPIB) for a Keihtley 236  for the
    characterization of nano-ionic memories.

    """

    def __init__(self, gpib_address=16,
                 compliance_level="1E-3",
                 measurement_range="1mA"):

        self._smu_ = pyvisa.ResourceManager().open_resource(f'GPIB0::{gpib_address}::INSTR',
                                                            write_termination='X\n',
                                                            )
        # Display message (max. 18 characters)
        self._display_user_message_('CONNECTION OK')
        time.sleep(3)

        # Return display to normal operation
        self._display_user_message_()

        self._factory_reset_()

        self._set_source_and_function_("V-I-dc")

        self._set_sense_("local")

        self._set_compliance_measurement_range_(compliance_level, measurement_range)

        self._set_integration_time_("20ms")

        self._set_filter_(32)

    def __del__(self):
        self._factory_reset_()
        self._set_integration_time_("20ms")
        self._set_filter_(32)
        self._smu_.close()

    def _arm_trigger_(self, mode):
        """
        Arm the trigger if the argument is true. Otherwise, the trigger will
        be disarmed.
        """

        if mode:
            self._smu_.write("R1")
        else:
            self._smu_.write("R0")

    def _display_user_message_(self, message=None):
        """
        Message is displayed on the screen of the SMU.
        (ASCII characters only, max. 18 characters).
        When None is passed, the screen returns to the default mode.
        """

        if message:
            self._smu_.write(f'D1,{message}')
        else:
            self._smu_.write('D0')

    def _write_(self, command):
        """Write command to GPIB interface."""

        self._smu_.write(command)

    def _query_(self, request):
        """Sends command as query to the GPIB interface."""

        return self._smu_.query(request)

    def _factory_reset_(self):
        """Restore factory defaults."""

        self._smu_.write('J0')

    def _over_compliance_(self):
        """
        Checks whether the compliance value has been exceeded.
         If the value was exceeded, an exception is triggered.
        """

        if self._smu_.stb == 128:
            raise Exception("Over compliance.")

    def _set_bias_(self, level, source_range="110V", delay=100):
        """
        Sets the bias voltage, the range and the delay
        (for the source-delay-measurement-cycle).

        :param level: float
            Specifies the de bias voltage [V].
        :param source_range: str
            Selects the bias range. Allowed values are: auto, 1.1V, 11V and 110V.
        :param delay: float
            The delay in milliseconds (0 to 65000).
        """

        if self._get_source_and_function_() != 'V-I-dc':
            raise NotImplementedError('The method set_bias() is only '
                                      'implemented for source and function: "V-I-dc".')

        ranges = {"auto": "0", "1.1V": "1", "11V": "2", "110V": "3"}

        if source_range not in ranges:
            raise ValueError('Bias could not be changed. Invalid source_range. '
                             f'Possible input values are: {", ".join(ranges.keys())}.')

        if not 0 <= delay <= 65000:
            raise ValueError('Bias could not be changed. Invalid delay. '
                             'Delay must be within 0-65000ms')

        self._set_trigger_(False)
        self._smu_.write(f"B{level},{ranges[source_range]},{delay}")
        self._set_trigger_(True)

    def _set_compliance_measurement_range_(self, compliance_level, measurement_range):
        """
        Sets the compliance level and measurement source_range.

        :param compliance_level: str
            Compliance value [A]. Scientific notation required e.g "1E-9" for 1nA.
            (Default value is 1E-9).
        :param measurement_range: str
            Measurement source_range for the current. Allowed values are: Auto, 1nA,
            10nA, 100nA, 1µA, 10µA, 100µA, 1mA, 10mA and 100mA. (Default value is 1nA).
        """

        if self._get_source_and_function_() != 'V-I-dc':
            raise NotImplementedError('The method set_compliance_measurement_range() is only '
                                      'implemented for source and function: "V-I-dc".')

        ranges = {"Auto": ["0", 1E-1],
                  "1nA": ["1", 1E-9],
                  "10nA": ["2", 1E-8],
                  "100nA": ["3", 1E-7],
                  "1µA": ["4", 1E-6],
                  "10µA": ["5", 1E-8],
                  "100µA": ["6", 1E-4],
                  "1mA": ["7", 1E-3],
                  "10mA": ["8", 1E-2],
                  "100mA": ["9", 1E-1]
                  }

        if measurement_range not in ranges:
            raise ValueError(f'Compliance and measurement source_range could not be'
                             f' changed. Invalid input. Possible input '
                             f'values are: {", ".join(ranges.keys())}.')

        if not 0 < float(compliance_level) <= ranges[measurement_range][1]:
            raise ValueError(f'The compliance voltage {compliance_level}A must be '
                             f'within the measurement source_range {measurement_range}.')

        self._set_trigger_(False)
        self._smu_.write(f'L{compliance_level},{ranges[measurement_range][0]}')
        time.sleep(0.01)
        self._set_trigger_(True)

    def _set_filter_(self, filter_value):
        """
        Sets the filter parameter, which specifies how many
         measurements are averaged for one data point.
        :param filter_value: int
            Allowed values 1, 2, 4, 8, 16, 32
        """

        filter_values = [1, 2, 4, 8, 16, 32]

        if filter_value not in filter_values:
            raise ValueError(f'Filter could not be changed. Invalid input. '
                             f'Possible input values '
                             f'{", ".join(list([str(x) for x in filter_values]))}.')

        self._smu_.write(f'P{int(math.log(filter_value, 2))}')

    def _set_integration_time_(self, value):
        """
        Sets the integration time for the measurement.

        :param value: str
            Allowed values are 416µs, 4ms, 16.67ms and 20ms.
        """

        values = {"416µs": "0", "4ms": "1", "16.67ms": "2", "20ms": "3"}

        if value not in values:
            raise ValueError('Integration time could not be changed. Invalid value. '
                             'Possible input values are: {}.'.format(", ".join(value.keys())))

        self._smu_.write(f"S{values[value]}")

    def _set_operate_(self, mode):
        """Switches the ouput on and off."""

        if mode is True:
            self._smu_.write("N1")
        elif mode is False:
            self._smu_.write("N0")
        else:
            raise ValueError('Parameter for _set_operate_ must be True or False.')

    def _set_output_data_format_(self, mode):
        """
        Sets the output data format for trigger queries. Allowed values are:
        no items, source value, delay value, measure value,
        source and measure value, time value, all values.
        """

        modes = {"no items": "0",
                 "source value": "1",
                 "delay value": "2",
                 "measure value": "4",
                 "source and measure value": "5",
                 "time value": "8",
                 "all values": "15",
                 }

        try:
            if mode not in modes:
                raise ValueError
        except ValueError:
            print('Output data format could not be changed. Invalid input. '
                  'Possible input values are: {}.'.format(", ".join(modes.keys())))

        self._smu_.write(f"G{modes[mode]},2,0")

    def _set_sense_(self, mode):
        """Sets the sense mode either to local or to remote."""

        modes = {"local": "O0", "remote": "O1"}

        if mode not in modes:
            raise ValueError(f'Sense could not be changed. Invalid input. '
                             f'Possible input values are: {", ".join(modes.keys())}.')

        self._smu_.write(modes[mode])

    def _get_source_and_function_(self):
        """Return the source mode e.g. V-I-dc."""

        modes = {"F0,0": "V-I-dc", "F0,1": "V-I-sweep", "F1,0": "I-V-dc", "F1,1": "I-V-sweep"}

        status = self._get_status_("measurement parameters")

        return modes[re.search(r"([F]\d[,]\d)", status).group(1)]

    def _set_source_and_function_(self, mode):
        """Sets the source mode. Allowed modes are: V-I-dc, V-I-sweep, I-V-dc and I-V-sweep."""

        modes = {"V-I-dc": "F0,0",
                 "V-I-sweep": "F0,1",
                 "I-V-dc": "F1,0",
                 "I-V-sweep": "F1,1",
                 }

        if mode not in modes:
            raise ValueError(f'Source and function could not be changed. '
                             f'Invalid input. Possible input values are: '
                             f'{", ".join(modes.keys())}.')

        self._smu_.write(modes[mode])

    def _get_status_(self, mode):
        """Queries the various status information of the smu.

        :param mode: str
            Selects the status information to query. Allowed values are:
            model number and firmware, error status, stored ASCII string,
            machine status, measurement parameters, compliance value,
            suppression value, calibration status, sweep size,warning status,
            first sweep point in compliance, sweep measure size.

        :return: str
            Queried status information.
        """

        modes = {"model number and firmware": "U0",
                 "error status": "U1",
                 "stored ASCII string": "U2",
                 "machine status": "U3",
                 "measurement parameters": "U4",
                 "compliance value": "U5",
                 "suppression value": "U6",
                 "calibration status": "U7",
                 "sweep size": "U8",
                 "warning status": "U9",
                 "first sweep point in compliance": "U10",
                 "sweep measure size": "U11",
                 }

        if mode not in modes:
            raise ValueError(f'Status could not be queried. Invalid input. '
                             f'Possible input values are: {", ".join(modes.keys())}.')

        return self._smu_.query(modes[mode])

    def _set_trigger_(self, mode):
        """
        True sets the trigger to source-delay-measurement-cycle
        (trigger starts source, e.g. for measurements.
        False sets the trigger to continuous (e.g. to apply bias).
        """

        if mode is True:
            self._smu_.write("T1,1,0,0")
        elif mode is False:
            self._smu_.write("T0,0,0,0")
        else:
            raise Exception('Parameter for _set_trigger_ must be True or False.')

    def _get_trigger_(self):
        """Returns the current trigger mode e.g. T4,1,0,0."""

        status = self._get_status_("machine status")
        return re.search(r"(T\d,\d,\d,\d)", status).group()

    def impulse(self, voltage, duration):
        """Applies the voltage [V] for the duration [s]."""

        print("Start Impuls")
        self._set_bias_(voltage)
        self._set_trigger_(False)
        self._arm_trigger_(True)
        # time.sleep(0.1)
        self._set_operate_(True)
        time.sleep(duration)
        self._set_operate_(False)
        self._over_compliance_()
        print("Ende Impuls")

    def measurement(self, voltage, delay=1):
        """
        Returns measured current [A] for the applied voltage [V].
        Before the measurement the voltage is applied for the duration
        specified by the delay [s].
        """

        self._set_bias_(voltage, delay=delay * 1000)
        self._set_trigger_(True)
        self._arm_trigger_(True)
        self._set_output_data_format_("measure value")
        self._set_operate_(True)
        self._smu_.timeout = (delay + 1) * 1000
        measured_current = float(self._smu_.query('H0'))
        self._smu_.timeout = 1 * 1E3
        self._set_operate_(False)
        self._arm_trigger_(False)
        self._over_compliance_()

        return measured_current
