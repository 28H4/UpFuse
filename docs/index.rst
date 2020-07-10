.. UpFuse - Characterization documentation master file, created by
   sphinx-quickstart on Thu Jul  9 10:12:28 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation: UpFuse - Characterization
=====================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Requirements
------------
- The script is based on PyVisa. This package requires a VISA interface in the background (`NI-VISA download via: ni.com <https://www.ni.com/de-de/support/downloads/drivers/download.ni-visa.html#346210/>`_)
- Driver for the GPIB-USB-interface (`NI-488.2 download via: ni.com <https://www.ni.com/de-de/support/downloads/drivers/download.ni-488-2.html#345631/>`_)


measurement.py
--------------
.. automodule:: measurement
   :members:

reset_smu.py
----------------
.. automodule:: reset_smu

Keithley236 API
---------------
.. autoclass:: SimpleKeithley236.Keithley236.Keithley236


