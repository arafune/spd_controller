# Measure the pulse overlapping by using Photodiode

As the time response of the phtoodiode is quite slow (~ 50 ps), the precise determination cannot be made. However, the information from this measurements may help.

pulse_overlap_PD.py

```
usage: pulse_overlap_PD.py [-h] --start START --step STEP --end END --output OUTPUT [--reset] [--with_fig]
                           --channel CHANNEL
                           [--ET] [--average AVERAGE] [--flip] [--socket] [--flipper_port FLIPPER_PORT]

options:
  -h, --help            show this help message and exit
  --start START         Start position in mm unit.
  --step STEP           Step in um unit.
  --end END             End position in mm unit
  --output OUTPUT       Output file name
  --reset               if set, the mirror moves to "mechanically zero" and then move to the "start position"
  --with_fig            if set, the corresponding display image file is saved.
  --channel CHANNEL     Channel number 1 or 2.
  --ET                  If set, interpolation ET mode.
  --average AVERAGE     Set average times in acquition. if 0, Sample mode is set.
  --flip                if True, use flipper
  --socket              if set, connect Oscilloscopy by socket (Ethernet).
  --flipper_port FLIPPER_PORT
                        COM port number must be set for Windows.
```

The number of avearge is 256 would be better than others, while this mode takes longer time.
