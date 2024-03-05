#!/usr/bin/env python3

"""Module for GDS3502 Oscilloscope (USB connection through pySerial)"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing_extensions import Literal
from pathlib import Path
from .. import Comm

Channel = Literal[1, 2]
Connection = Literal["usb", "socket"]


class GDS3502(Comm):
    def __init__(self, term: str = "\n", connection: Connection = "usb") -> None:
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
        self.header_dict: dict[str, float | str] = {}
        if connection == "usb":
            port = self.connect_usb("GEV150786")
            self.connection: Connection = connection
            self.memory: NDArray[np.float_]
            if port:
                self.open(baud=115200, port=port)
                self.is_portopen = True
                return None
            raise RuntimeError("Not found")
        elif connection == "socket":
            self.connection = "socket"
            self.open_socket(("144.213.126.10", 3000), timeout=1, baud=115200)
            return None

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

    def reset(self) -> None:
        self.sendtext(":CHANnel1IMPedance?")
        impedance_1 = float(self.comm.readline())
        self.sendtext(":CHANnel2IMPedance?")
        impedance_2 = float(self.comm.readline())
        self.sendtext("*RST")
        self.sendtext(":CHANnel1:IMPedance {}".format(impedance_1))
        self.sendtext(":CHANnel2:IMPedance {}".format(impedance_2))
        self.sendtext(":AUTOSet")

    def set_impedance(self, channel: Channel, impedance: float = 5.0e1) -> None:
        self.sendtext(":CHANnel{}:IMPedance {}".format(channel, impedance))

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
        self.sendtext(":MEASure:SOURce CH{}".format(channel))
        self.sendtext(":MEASure:FREQuency?")
        return float(self.recvtext())

    def set_average_mode(self, n_average: int = 256) -> float:
        """Set average mode.

        This oscilloscope has 4 modes: Sample, HiResolution (boxcar smoothing), PeakDetec and Average.

        The Average mode would be more better than the Sample (default) mode.

        Different from the other modes, return the recommended waiting time.
        """
        self.sendtext(":ACQuire:MODe AVERage")
        assert n_average in (2, 4, 8, 16, 32, 64, 128, 256)
        waiting_time: dict[int, float] = {
            2: 2,
            4: 2,
            8: 2,
            16: 5,
            32: 10,
            128: 20,
            256: 40,
        }
        self.sendtext(f":ACQuire:AVERage {n_average}")
        return waiting_time[n_average]

    def set_hires_mode(self) -> None:
        """Set HiResolution mode

        This oscilloscope has 4 modes: Sample, HiResolution (boxcar smoothing), PeakDetec and Average.

        The HiResolution mode would not be more better than the Sample (default) mode, but for completeness, this method has been prepared.
        """
        self.sendtext(":ACQuire:MODe HIR")

    def set_peak_detect_mode(self) -> None:
        """Set Peak Detect Mode mode

        This oscilloscope has 4 modes: Sample, HiResolution (boxcar smoothing), PeakDetec and Average.

        The Peak Detect mode would not be more better than the Sample (default) mode, but for completeness, this method has been prepared.
        """
        self.sendtext(":ACQuire:MODe PDET")

    def set_sample_mode(self) -> None:
        """Set Peak Detect Mode mode

        This oscilloscope has 4 modes: Sample, HiResolution (boxcar smoothing), PeakDetec and Average.

        The Sample mode is the default mode of this oscilloscope.
        """
        self.sendtext(":ACQuire:MODe SAMP")

    def set_interpolation_et(self) -> None:
        """Set Interporation ET mode."""
        self.sendtext(":ACQuire:INTERpolation ET")

    def set_realtime_sampling(self) -> None:
        """Set Interporation ET mode."""
        self.sendtext(":ACQuire:INTERpolation SINC")

    def save_image(self, filename: str) -> None:
        """SaveImage data.

        The image file is png. (BMP is also available, but PNG would be better.)
        The filename suffix should be the capital. (.PNG)
        """
        self.sendtext(":SAV:IMAG:FILEF PNG")
        filename = "Disk:/" + Path(filename).stem + Path(filename).suffix.upper()
        self.sendtext(f':SAV:IMAGe "{filename}"')

    def acquire_memory(self, channel: Channel) -> NDArray[np.float_]:
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
        result_array: list[bytes] = self.comm.readlines()
        result = b"".join(result_array)
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
