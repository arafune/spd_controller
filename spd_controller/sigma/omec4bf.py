"""OMEC-4BF (OPT MIKE-E Controller)

Hardware specification:

"""

from __future__ import annotations
from typing import Literal

from serial.tools import list_ports

from .. import Comm

from enum import Enum


class Axis(Enum):
    X = 1
    Y = 2
    BOTH = 3


class OMEC4BF(Comm):
    """Class for OMEC-4BF controller.

    Parameters
    ----------
    term: str, optional
        termination character (default: CRLF)
    port: str, optional
        port name
    """

    def __init__(self, term: str = "\r\n", port: str = "") -> None:
        """Initialize."""
        super().__init__(term=term)
        self.open(tty=port, baud=9600)

    def status(self, group: Literal[1, 2]) -> str:
        command = f"{group}Q"
        self.sendtext(command)
        return self.recvtext()

    def position(self, group: Literal[1, 2], axis: Literal["x", "y"] | Axis) -> float:
        if isinstance(axis, str):
            axis_int = Axis[axis.upper()]
        assert isinstance(axis, Axis)
        axis_int = axis.value

    def abs_move(
        self,
        group: Literal[1, 2],
        axis: Literal["x", "y", "both"] | Axis,
        position: int,
    ) -> None:
        if isinstance(axis, str):
            axis_int = Axis[axis.upper()]
        assert isinstance(axis, Axis)
        axis_int = axis.value

    def rel_move(
        self,
        group: Literal[1, 2],
        axis: Literal["x", "y", "both"] | Axis,
        movement: int,
    ) -> None:
        if isinstance(axis, str):
            axis_int = Axis[axis.upper()]
        assert isinstance(axis, Axis)
        axis_int = axis.value
