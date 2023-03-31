#!/usr/bin/env python
"""Class for Prodigy remote_in"""

import socket

from .. import SocketClient

BUFSIZE = 1024


class RemoteIn(SocketClient):
    """Class for Prodigy Remote In"""

    def __init__(self, host: str, port: int) -> None:
        super().__init__(host="146.126.148.140", port=7010)
        self.id: int = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def sendtext(self, text: str) -> int:
        """An syntax suger of sendtext

        To send the command to Remote_In Prodigy, the text is converted to byte with linefeed character self.

        Parameters
        ------------
        text: str
            input text

        Returns
        --------
        int: number of byte send
        """
        text = text + "\n"
        return self.socket.send(text.encode("utf-8"))

    def sendcommand(self, text: str) -> int:
        """Send command"""
        request_str: str = "?" + format(self.id, "04X") + text
        self.id += 1
        return self.sendtext(request_str)

    def recvtext(self, byte_size: int) -> str:
        """"""
        return self.socket.recv(byte_size).decode("utf-8")

    def connect(self) -> str:
        """Open connection to SpecsLab Prodigy

        Returns
        --------
        str: Responce of "Connect command"
            OK: ServerName: <> ProtocolVersion: <Major.Minor>
        """
        self.sendcommand("Connect")
        return self.recvtext(BUFSIZE)

    def disconnect(self) -> str:
        """Close connection to SpecsLab Prodigy

        Returns
        --------
        str: Responce of "Disconnect command"
            OK
        """
        self.sendcommand("Disonnect")
        return self.recvtext(BUFSIZE)

    def defineFAT(
        self,
        start_energy: float,
        end_energy: float,
        step: float,
        dwell: float = 0.096,
        pass_energy: float = 5,
        lens: str = "WideAngleMode",
        scanrange: str = "40 V",
    ) -> str:
        command: str = 'DefineSpectrumFAT StartEnergy:{} EndEnergy:{} StepWidth:{} DwellTime:{} PassEnergy:{} LensMode:"{}" ScanRange"{}"'.format(
            start_energy, end_energy, step, dwell, pass_energy, lens, scanrange
        )
        self.sendcommand(command)
        return self.recvtext(BUFSIZE)

    def defineSFAT(
        self,
        start_energy: float,
        end_energy: float,
        samples: int,
        dwell: float = 0.096,
        lens: str = "WideAngleMode",
        scanrange: str = "40 V",
    ) -> str:
        command: str = 'DefineSpectrumSFAT StartEnergy:{} EndEnergy:{} Samples:{} DwellTime:{} LensMode:"{}" ScanRange"{}"'.format(
            start_energy, end_energy, samples, dwell, lens, scanrange
        )
        self.sendcommand(command)
        return self.recvtext(BUFSIZE)

    def checkFAT(
        self,
        start_energy: float,
        end_energy: float,
        step: float,
        dwell: float = 0.096,
        pass_energy: float = 5,
        lens: str = "WideAngleMode",
        scanrange: str = "40 V",
    ) -> str:
        command: str = 'CheckSpectrumFAT StartEnergy:{} EndEnergy:{} StepWidth:{} DwellTime:{} PassEnergy:{} LensMode:"{}" ScanRange"{}"'.format(
            start_energy, end_energy, step, dwell, pass_energy, lens, scanrange
        )
        self.sendcommand(command)
        return self.recvtext(BUFSIZE)

    def checkSFAT(
        self,
        start_energy: float,
        end_energy: float,
        samples: int,
        dwell: float = 0.096,
        lens: str = "WideAngleMode",
        scanrange: str = "40 V",
    ) -> str:
        command: str = 'CheckSpectrumSFAT StartEnergy:{} EndEnergy:{} Samples:{} DwellTime:{} LensMode:"{}" ScanRange"{}"'.format(
            start_energy, end_energy, samples, dwell, lens, scanrange
        )
        self.sendcommand(command)
        return self.recvtext(BUFSIZE)

    def validate(self) -> str:
        self.sendcommand("ValidateSpectrum")
        return self.recvtext(BUFSIZE)

    def start(self, setsafeafter: bool = True) -> str:
        if setsafeafter:
            command: str = "Start"
        else:
            command = 'Start SetSafeStartAfter:"false"'

        self.sendcommand(command)
        return self.recvtext(BUFSIZE)

    def clear(self) -> str:
        self.sendcommand("ClearSpectrum")
        return self.recvtext(BUFSIZE)

    def get_status(self) -> str:
        self.sendcommand("GetAcquisitionStatus")
        return self.recvtext(BUFSIZE)

    def save_data(self) -> None:
        pass
