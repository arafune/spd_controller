# Measure the pulse overlapping by using Photodiode

As the time response of the phtoodiode is quite slow (~ 50 ps), the precise determination cannot be made. However, the information from this measurements may help.

pulse_overlap_PD.py

```
usage: pulse_overlap_PD.py [-h] --start START --step STEP --end END --output OUTPUT [--reset] [--with_fig] --channel CHANNEL [--average AVERAGE]
                           [--flip]

options:
  -h, --help         show this help message and exit
  --start START      Start position in mm unit.
  --step STEP        Step in um unit.
  --end END          End position in mm unit
  --output OUTPUT    Output file name
  --reset            if set, the mirror moves to "mechanically zero" and then move to the "start position"
  --with_fig         if set, the corresponding display image file is saved.
  --channel CHANNEL  Channel number 1 or 2.
  --average AVERAGE  Set average times in acquition. if 0, Sample mode is set.
  --flip             if True, use flipper
```

The number of avearge is 256 would be better than others, while this mode takes longer time.
