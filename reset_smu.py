"""Simple script to reset the Keithley236 to its factory defaults."""

from SimpleKeithley236.Keithley236 import Keithley236

if __name__ == '__main__':
    smu = Keithley236(16, 'Auto', None)
