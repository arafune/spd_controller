#!/usr/bin/env python3
"""Module for GDS3502 Oscilloscope (socket connection)"""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from .. import TcpSocketWrapper

Channel = Literal[1, 2]


class GDS3502:
    """_summary_"""

    def __init__(
        self,
        host: str = "144.213.126.10",
        port: int = 3000,
        term: Literal["\n", "\r", "\r\n"] = "\n",
        verbose=False,
    ) -> None:
        """Initialization of the GDS3502 (socket version)

        Parameters
        ----------
        host : str, optional
            hostname or IP address, by default "144.213.126.10"
        port : int, optional
            port number of socket server, by default 3000
        term : str, optional
            line termination character, by default "\n"
        verbose : bool, optional
            if true, the verbose mode, by default False
        """
        self.name: str = "GDS3502"
        self.host: str = host
        self.port: int = port
        self.TERM: Literal["\n", "\r", "\r\n"] = term
        self.timeout = 2
        self.verbose: bool = verbose
        self.header: dict[str, float | str] = {}
        self.memory: NDArray[np.float_]
        self.connection = "socket"

    def connect(self):
        """Connect the texio GDS3501"""
        self.sock = TcpSocketWrapper(term=self.TERM, verbose=self.verbose)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

    def lrn(self) -> str:
        """Returns the oscilloscope settings as a data string

        Returns
        -------
        str
            Oscilloscope setting
        """
        self.sock.sendtext("*LRN?")
        return self.sock.makefile(mode="rb").readline().decode("utf-8")

    def reset(self) -> None:
        self.sock.sendtext(":CHANnel1IMPedance?")
        impedance_1 = float(self.sock.recvtext(1024))
        self.sock.sendtext(":CHANnel2IMPedance?")
        impedance_2 = float(self.sock.recvtext(1024))
        self.sock.sendtext("*RST")
        self.sock.sendtext(":CHANnel1:IMPedance {}".format(impedance_1))
        self.sock.sendtext(":CHANnel2:IMPedance {}".format(impedance_2))
        self.sock.sendtext(":AUTOSet")

    def set_impedance(self, channel: Channel, impedance: float = 5.0e1) -> None:
        self.sock.sendtext(":CHANnel{}:IMPedance {}".format(channel, impedance))

    def measure_frequency(self, channel: Channel) -> float:
        """Measure the frequency from the channel.

        [TODO:description]

        Parameters
        ----------
        channel: Channel
            [TODO:description]

        Returns
        -------
        float
            Measured frequency
        """
        self.sock.sendtext(":MEASsure:SOURce1  CH{}".format(channel))
        self.sock.sendtext(":MEASsure:FREQuency?")
        return float(self.sock.recvtext(1024))

    def acquire_memory(self, channel: Channel) -> NDArray:
        """Return the memory

        Parameters
        ----------
        channel : Channel
            Channel number (1 or 2)

        Returns
        -------
        NDArray[np.float]
            Oscilloscope data
        """
        self.sock.sendtext(":ACQuire{}:MEMory?".format(channel))
        result = self.sock.makefile(mode="rb").readline()
        data_index: int = result.find(b"#550000") + 7
        header = result[:data_index].decode("utf-8")
        wave_data = result[data_index:-1]
        for i in header.split(";")[:-2]:
            k, v = i.split(",")
            try:
                self.header[k] = int(v)
            except ValueError:
                try:
                    self.header[k] = float(v)
                except ValueError:
                    self.header[k] = v
        wave = [[wave_data[i], wave_data[i + 1]] for i in range(0, len(wave_data), 2)]
        timescale: NDArray[np.float64] = np.linspace(
            0,
            float(self.header["Sampling Period"]) * float(self.header["Memory Length"]),
            int(self.header["Memory Length"]),
            endpoint=False,
        )
        amplitudes: list[int] = []
        for points in wave:
            if points[0] == 0:
                amplitudes.append(points[1])
            else:
                amplitudes.append(-1 * (int(bin(~points[1] & 0xFF), 0)))
        self.timescale = timescale
        self.memory = np.array(
            np.array(amplitudes) * self.header["Vertical Scale"] / 25
        )
        return self.memory
