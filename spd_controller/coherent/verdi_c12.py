from __future__ import annotations
import contextlib
from typing import Literal

from .. import TcpSocketWrapper


class MockVerdiC12:
    """Mock of Verdi C12"""

    def __init__(self):
        pass


class VerdiC12:
    """Coherent Pump laser Verdi C12 class"""

    def __init__(
        self,
        host: str = "144.213.126.108",
        port: int = 23,
        name: str = "VerdiC12",
        timeout: int = 2,
        *,
        verbose: bool = False,
    ) -> None:
        self.name = name
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        self.sock: TcpSocketWrapper | None = None

    def connect(self) -> None:
        """Connect Verdi C12 via TCPIP."""
        self.sock = TcpSocketWrapper(term="\r\n", verbose=self.verbose)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))
        #
        self.cmd("PROMPT=0")

    def cmd(self, cmd: str) -> int:
        """Send a command to veridi C12

        Parameters
        -----------
        cmd: str
            command with argument
        """
        cmdstr = f"{cmd}\r\n"
        assert self.sock is not None
        return self.sock.send(cmdstr.encode("utf-8"))

    def ask(self, cmd: str) -> bytes:
        self.cmd(cmd)
        assert self.sock is not None
        answer = self.sock.recv(1024)
        while answer[-2:] != b"\r\n":
            an_reply = self.sock.recv(1024)
            answer += an_reply
        return answer
