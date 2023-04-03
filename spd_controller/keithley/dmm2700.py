#!/usr/bin/env python3
"""Read voltage from Keithley 2700

"""

from __future__ import annotations

import datetime
from time import sleep

from serial.tools import list_ports

from .. import Comm


class DMM2700(Comm):
    def __init__(self, port: str = "") -> None:
        super().__init__()
        ttys = [port.devie for port in list_ports.comports()]
        for tty in ttys:
            self.open(tty=tty, baud=19200, xonxoff=True)
            self.sendtext("*IDN?")
            return_info = self.recvtext().strip()
            if return_info.startswith("KEITHLEY INSTRUMENTS INC.,MODEL 2700"):
                self.is_portopen = True
                self.close()
                self.open(tty=tty, baud=19200, xonxoff=True)
                self.sendtext("*RST")
                self.sendtext("*CLS")
                return None
            else:
                self.close()
        raise RuntimeError("Check the port. Cannot find the connection to K2700")

    def wait_for_srq(self, command: str) -> bool:  # At present, not work well.
        """Waits for a service request from the K2700.

        The service request must be enable on the instrument prior to calling this"""
        self.sendtext(command)
        self.sendtext("*STB?")
        stb: str = self.recv()[1].decode("utf-8").strip()
        while stb != 0:
            sleep(1)
            self.sendtext("command")
            self.sendtext("*STB?")
            stb = self.recv()[1].decode("utf-8").strip()
        self.sendtext("*SRE 48")
        return True

    def conf_voltage(self) -> None:
        """Configure voltage measurement."""
        # self.wait_for_srq("*SRE 1;:STAT:MEAS:ENAB 32;*CLS;")
        self.sendtext(":SENS:VOLT:NPLC 5")  # "slow" に対応
        self.sendtext(":SENS:VOLT:RANG 10")
        self.sendtext(":SENS:VOLT:RANG:AUTO OFF")
        self.sendtext(
            "VOLT:AVER:TCON MOV;:VOLT:AVER:COUN 20;:VOLT:AVER ON"
        )  ## 平均は2ぐらいが適当？ しなくてもよい？
        self.sendtext("VOL:DC:AVER:WIND 10")
        self.sendtext(":FORM ASC;:FORM:ELEM READ")

    def measure(self) -> float | None:
        """Return the voltage:

        This query (MEAS?) is much slower than a :READ? or :FETCh? query
        because it has to reconfigure the instrument each time it is sent.
        It will reset the NPLC, autoranging, and averaging to default settings.
        """
        self.sendtext("READ?")
        voltage: bytes
        _, voltage = self.recv()
        try:
            return float(voltage.decode("utf-8").strip())
        except (ValueError, UnicodeDecodeError):
            print(voltage)
            return None


if __name__ == "__main__":
    k = DMM2700()
    k.conf_voltage()
    for i in range(10):
        now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        print("{} {}".format(now, k.measure()))
    k.close()
