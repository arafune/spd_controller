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

    def defineFAT(self) -> str:
        pass

    def defineSFAT(self) -> str:
        pass

    def checkFAT(self) -> str:
        pass

    def checkSFAT(self) -> str:
        pass

    def validate(self) -> str:
        pass

    def start(self) -> str:
        pass

    def clear(self) -> str:
        pass

    def get_state(self) -> str:
        pass

    def save_data(self) -> None:
        pass
