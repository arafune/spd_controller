#!/usr/bin/env python3

"""Module for GDS3502 Oscilloscope (socket connection)"""

from __future__ import annotations

import socket

import numpy as np
from numpy.typing import NDArray
from typing_extensions import Literal

from .. import SocketClient

Channel = Literal[1, 2]


class GDS3502(SocketClient):
    def __init__(
        self, host: str = "144.213.126.10", port: int = 3000, term: str = "\n"
    ) -> None:
        """_summary_

        Parameters
        ----------
        term : str, optional
            _description_, by default "\n"

        Raises
        ------
        RuntimeError
            _description_
        """
        super().__init__(host=host, port=port, term=term)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.header: dict[str, float | str] = {}
        self.memory: NDArray[np.float_]

    def lrn(self) -> str:
        """Returns the oscilloscope settings as a data string

        Returns
        -------
        str
            Oscilloscope setting
        """
        self.sendtext("*LRN?")
        return self.recvline(128)

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
        self.sendtext(":ACQuire{}:MEMory?".format(channel))
        result = self.recvline(8192)
        data_index: int = result.find("#550000") + 7
        header = result[:data_index]
        wave_data = result[data_index:-1].encode("utf-8")
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
