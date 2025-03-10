"""OMEC-4BF (OPT MIKE-E Controller)

Hardware specification:

"""

from __future__ import annotations
from typing import Literal, TypedDict

from serial.tools import list_ports

from .. import Comm

from enum import Enum

VERBOSE = False


class Axis(Enum):
    X = 1
    Y = 2
    BOTH = 3


class _OMECStatus(TypedDict, total=True):
    x: int
    y: int
    x_condition: Literal["N", "+", "-", "O"]
    y_condition: Literal["N", "+", "-", "O"]
    ready: bool
    command_err: Literal["NN", "E1", "E3", "E5", "E7"]
    extend_to_edge: bool


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

    def status(self, group: Literal[1, 2]) -> _OMECStatus:
        command = f"{group}Q"
        self.sendtext(command)
        status = self.recvtext().strip().split(",")
        status_dict: _OMECStatus = {
            "x": 0,
            "y": 0,
            "x_condition": "N",
            "y_condition": "N",
            "ready": False,
            "command_err": "NN",
            "extend_to_edge": False,
        }
        status_dict["x"] = int(status[0])
        status_dict["y"] = int(status[1])
        status_dict["x_condition"] = status[2]
        status_dict["y_condition"] = status[3]
        status_dict["ready"] = True if status[4] == "N" else False
        status_dict["command_err"] = status[5]

        return status_dict

    def check_stop(self, group: Literal[1, 2]) -> bool:
        """Return True if the motor stops (Not-busy).

        Returns
        -------
        bool
            True if the motor stops.
        """
        return self.status(group)["ready"]

    def position(self, group: Literal[1, 2], axis: Literal["x", "y"]) -> int:
        status = self.status(group)
        return status[axis.lower()]

    def moving(self, group: Literal[1, 2]) -> tuple[int, int] | None:
        """Check the current stage condition.

        Returns
        -------
        tuple[int, int] | None
            the current position, if the stage is not moving, return None
        """
        status = self.status(group)
        if status["ready"]:
            return status["x"], status["y"]
        else:
            return None

    def wait_during_move(
        self,
        group: Literal[1, 2] = 1,
        *,
        printing: bool = False,
    ) -> None:
        """Wait moving ends.

        Parameters
        ----------
        printing: bool
            if True, print the "current" position

        """
        current_position: tuple[int, int] | None = self.moving(group)
        while current_position:
            if printing:
                print(
                    f"current_position(x): {current_position[0]}, current_position(y): {current_position[1]}"
                )
            current_position = self.moving(group)

    def move_abs(
        self,
        group: Literal[1, 2] = 1,
        axis: Literal["x", "y", "both"] | Axis = "x",
        position: int = 0,
        *,
        wait: bool = True,
    ) -> None:
        """Move to the absolute position.

        Parameters
        ----------
        group
            [TODO:description]
        axis
            [TODO:description]
        position
            [TODO:description]
        wait
            if True, wait for finihsing the moving.
        """
        axis_int = axis_int = (
            Axis[axis.upper()] if isinstance(axis, str) else axis.value
        )
        cmd = f"{group}A{axis_int}:{position}"
        self.sendtext(cmd)
        if wait:
            self.wait_during_move(group=group, printing=VERBOSE)

    def move_origin(
        self, group: Literal[1, 2] = 1, axis: Literal["x", "y", "both"] | Axis = "x"
    ) -> None:
        axis_int = axis_int = (
            Axis[axis.upper()] if isinstance(axis, str) else axis.value
        )
        cmd = f"{group}H{axis_int}"
        self.sendtext(cmd)
        self.wait_during_move(group=group, printing=VERBOSE)

    def move_rel(
        self,
        group: Literal[1, 2] = 1,
        axis: Literal["x", "y", "both"] | Axis = "x",
        move: int = 0,
        *,
        wait: bool = True,
    ) -> None:
        """Move to the absolute position.

        Parameters
        ----------
        group
            [TODO:description]
        axis
            [TODO:description]
        position
            [TODO:description]
        wait
            if True, wait for finihsing the moving.
        """
        axis_int = axis_int = (
            Axis[axis.upper()] if isinstance(axis, str) else axis.value
        )
        cmd = f"{group}M{axis_int}:{move}"
        self.sendtext(cmd)
        if wait:
            self.wait_during_move(group=group, printing=VERBOSE)
