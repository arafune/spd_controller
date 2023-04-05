#!/usr/bin/env python3

"""Module for GDS3502 Oscilloscope (USB connection through pySerial)"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing_extensions import Literal

from .. import Comm

Channel = Literal[1, 2]


class GDS3502(Comm):
    def __init__(self, term: str = "\n") -> None:
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
        super().__init__(term=term)
        port = self.connect("GEV150786")
        self.connection = "usb"
        self.header_dict: dict[str, float | str] = {}
        self.memory: NDArray[np.float_]
        if port:
            self.open(baud=115200, port=port)
            self.is_portopen = True
            return None
        raise RuntimeError("Not found")

    def lrn(self) -> str:
        """Returns the oscilloscope settings as a data string

        Returns
        -------
        str
            Oscilloscope setting
        """
        self.sendtext("*LRN?")
        tmp: list[bytes] = self.comm.readlines()
        return_info: bytearray = bytearray()
        for a in tmp:
            return_info += a
        return return_info.decode("utf-8")

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
        result: bytearray = bytearray(self.comm.readlines())
        data_index: int = 7 + result.find(b"#550000")
        header = result[:data_index].decode("utf-8")
        wave_data = result[data_index:-1]
        for i in header.split(";")[:-2]:
            k, v = i.split(",")
            try:
                self.header_dict[k] = int(v)
            except ValueError:
                try:
                    self.header_dict[k] = float(v)
                except ValueError:
                    self.header_dict[k] = v
        wave = [[wave_data[i], wave_data[i + 1]] for i in range(0, len(wave_data), 2)]
        timescale: NDArray[np.float64] = np.linspace(
            0,
            float(self.header_dict["Sampling Period"])
            * float(self.header_dict["Memory Length"]),
            int(self.header_dict["Memory Length"]),
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
            np.array(amplitudes) * self.header_dict["Vertical Scale"] / 25
        )
        return self.memory
