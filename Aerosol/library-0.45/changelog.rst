Changelog
=========

Unreleased
----------

0.4.3 - 2020-03-06
------------------
Fixed
~~~~~
- Dynamic background noise removal out of range issue
- Lidar tilt adjustment out of range

0.4.2 - 2020-02-09
------------------
Fixed
~~~~~
- numpy floating cap issue
- File directory fix for Mac OS/Debian environment

0.4.1 - 2020-02-01
------------------
Added
~~~~~
- Channel selection for old LB100 model

0.4.1 - 2018-11-29
------------------
Added
~~~~~
- Support for Python 3

Fixed
~~~~~
- Bug in Licel2depol script, wrong handling of dark measurements.
- Wrong number of timescales in depolarization calibration netcdf files.

0.3.5 - 2018-10-10
------------------
Fixed
~~~~~
- Bug in Licel2depol script.

Removed
~~~~~~~
- Experimental cloud mask script. It will be soon released in the SCC interface.


0.3.4 - 2018-03-22
------------------
Fixed
~~~~~
- Added First_Signal_Rangebin in supported channel variables.

Added
~~~~~
- Plotting of cloud-mask

0.3.3 - 2018-03-18
------------------
Fixed
~~~~~
- Fixed bug when saving SCC NetCDF file.
- Fixed confusing error message when saving SCC NetCDF and Laser_Shots are read from Licel file.

0.3.2 - 2018-02-28
------------------
Fixed
~~~~~
- Fixed installation of non-wheel package

0.3.0 - 2018-02-28
------------------
Fixed
~~~~~
- Bug when calculating physical units for Licel analog signals

Added
~~~~~
- Initial support of Raymetrics scanning files.
- Initial experimental support of cloud masking when converting licel to SCC format.
- Added support for overlap and lidar ratio file names in SCC format.


Changed
~~~~~~~
- Improvements on DIVA format.

0.2.14 - 2018-01-10
-------------------
Fixed
~~~~~
- Correct reading of measurement parameters from Licel files.
- Fixed possible problems with class-level parameters in Licel measurement class.

Added
~~~~~
- First ideas for a DIVA netCDF format.