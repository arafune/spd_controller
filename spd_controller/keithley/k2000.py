#!/usr/bin/env python3
"""Read voltage from Keithley 2000

Caution: An old DMM K2000 dows not work with RS232. """
from __future__ import annotations

import argparse
import datetime
from time import sleep

from serial.tools import list_ports

from .. import Comm


class K2000(Comm):
    def __init__(self) -> None:
        super().__init__()
        ttys = [port.device for port in list_ports.comports()]
        for tty in ttys:
            self.open(tty=tty, baud=19200)
            self.sendtext("*IDN?")
            return_info = self.recvtext().strip()
            if return_info.startswith("KEITHLEY INSTRUMENTS INC.,MODEL 2000"):
                self.is_portopen = True
                self.close()
                self.open(tty=tty, baud=19200)
                self.sendtext("*RST")
                self.sendtext("*CLS")
                return None
            else:
                self.close()
        raise RuntimeError("Check the port. Cannot find the connection to K2000")

    def wait_for_srq(self, command: str) -> bool:
        """Waits for a service request from K2000.

        The service request must be enable on the instrument prior to calling this"""
        self.sendtext(command)
        self.sendtext("*STB?")
        stb = int(self.read(10).decode("utf-8").strip())
        while stb != 0:
            sleep(1)
            self.sendtext("command")
            self.sendtext("*STB?")
            stb = int(self.recv()[1].decode("utf-8").strip())
        self.sendtext("*SRE 48")
        return True

    def measure(self) -> float:
        """Meaurement

        From Data Read Single.vi
        """
        self.wait_for_srq("*SRE 1;:STAT:MEAS:ENAB 32;*CLS;")
        self.sendtext(":FORM ASC;:FORM:ELEM READ;:SENS:DATA?")
        read = self.read(100)
        return float(read.decode("utf-8").strip())


if __name__ == "__main__":
    k = K2000()
    k.wait_for_srq("*SRE 1;:STAT:MEAS:ENAB 32;*CLS;")
    while True:
        print(k.measure())
        k.sendtext(":SAMP:COUN?")
        _, count = k.recv()
        print(count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--output",
        metavar="file_name",
    )
    args = parser.parse_args()

    if args.output is not None:
        exit
        # args.poscar.save(args.output)

    comm = Comm()
    comm.open(tty="/dev/ttyUSB0", baud=2400)
    comm.sendtext("*RST")
    comm.sendtext("*CLS")
    # Setting
    comm.sendtext(":INIT:CONT ON;:ABORT")
    comm.sendtext("CONF:VOLT:DC")
    # comm.sendtext("SENS:AZER:STAT OFF")
    comm.sendtext("VOLT:NPLC 6")
    comm.sendtext("VOLT:RANGE 1")  # << controllable?
    comm.sendtext(":SENS:VOLT:DC:DIG 7")
    comm.sendtext(":FORM:ELEM READ")
    # comm.sendtext(":DISP:ENAB OFF")

    if args.output is not None:
        with open(args.output, mode="w") as f:
            while True:
                comm.sendtext("READ?")
                result, data = comm.recv(10)
                now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                f.write("{}\t{}\n".format(now, data.decode("utf-8")))
    else:
        while True:
            comm.sendtext("MEASURE?")
            # result, data = comm.recv(1)
            data = comm.recvbytes()
            now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            if len(data) < 5:
                comm.sendtext("MEASURE?")
                data = comm.recvbytes()
                now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            try:
                print("{}\t{}".format(now, data.decode("utf-8")))
            except UnicodeDecodeError:
                print(data)
                comm.sendtext("*CLS")
    comm.close()  ## Actually knot work. でも将来 Ctrl-C で止めるときのことを考えて・・・
