#!/usr/bin/env python3
"""Keithley 6514 から電流値を読み取る"""

import argparse
import datetime

from simpleComm import Comm

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    "--output",
    metavar="file_name",
    help="""output file name
if not specified, use standard output""",
)
args = parser.parse_args()


comm: Comm = Comm()
comm.open(tty="/dev/ttyUSB0", baud=57600)
comm.sendtext("*RST")
comm.sendtext("*CLS")
# Setting
comm.sendtext("CONF:CURR")
comm.sendtext("CURR:RANG 2.1e-5")  # << controllable?
comm.sendtext("AVER OFF")
comm.sendtext("DISP:DIG 7")
comm.sendtext("FORM:ELEM READ")
comm.sendtext("DISP:ENAB OFF")
comm.sendtext("INIT")
if args.output is not None:
    with open(args.output, mode="w") as f:
        while True:
            comm.sendtext("READ?")
            result, data = comm.recv(10)
            now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            f.write("{}\t{}\n".format(now, data.decode("utf-8")))
else:
    while True:
        comm.sendtext("READ?")
        result, data = comm.recv(10)
        now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        print("{}\t{}".format(now, data.decode("utf-8")))
comm.close()  ## Actually not work.
