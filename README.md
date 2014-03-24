plottool
========

This script is intended to be used with a serial connected plotter/cutter.

It will split the file into blocks <=10kB to prevent the plotter from choking on data.

usage is simple:

```./plottool file.hpgl``` will simply print the data to ```/dev/ttyUSB0```

```./plottool -p /dev/ttyUSB4 file.hpgl``` will do the same but to port ```/dev/ttyUSB4```

this script has been tested with a plotter @Stratum0: https://stratum0.org/wiki/Cogi_CT-630