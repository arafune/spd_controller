#!/usr/bin/python3
"""SMC HECR Chiller"""


from __future__ import annotations

import argparse

from serial.tools import list_ports

from .. import Comm


class HECR(Comm):
    """Class for HECR Chiller

    Parameters
    -----------
    term: str
        termination character (default is )

    port: str
        port name

    Raises
    -------
    RuntimeError:
        Occurs when no port can be found.
    """

    def __init__(self, term: str = "\r", port="") -> None:
        """Initialize"""
        super().__init__(term=term)
        if port:
            self.open(tty=port, baud=9600)
        else:
            ttyes = [port.device for port in list_ports.comports()]
            for tty in ttyes:
                self.open(tty=tty, baud=9600)
