"""OMEC-4BF (OPT MIKE-E Controller)

Hardware specification:

"""

from __future__ import annotations
from typing import Literal, TypedDict

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
        """Retrieves the status of the specified group.

        Args:
            group (Literal[1, 2]): The group number (1 or 2).

        Returns:
            _OMECStatus: A dictionary containing the status information.
        """

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

    def position(self, group: Literal[1, 2], axis: Literal["x", "y"]) -> int:
        """
        Gets the position of the specified axis for the given group.

        Args:
            group (Literal[1, 2]): The group number (1 or 2).
            axis (Literal["x", "y"]): The axis ("x" or "y").

        Returns:
            int: The position of the specified axis.
        """
        status = self.status(group)
        return status[axis.lower()]

    def wait_during_move(
        self,
        group: Literal[1, 2] = 1,
        *,
        printing: bool = False,
    ) -> None:
        """Wait for the move operation to complete.

        This method blocks the excecution until the move operation is finished.

        Parameters
        ----------
        group : Literal[1, 2]
            The group number (1 or 2), by default 1.
        printing: bool
            if True, print the "current" position

        """
        status = self.status(group=group)
        while not status["ready"]:
            if printing:
                print(
                    f"current_position(x): {status['x']}, current_position(y): {status['y']}"
                )
            status = self.status(group)

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
        group : Literal[1, 2], optional
            The group number (1 or 2), by default 1.
        axis : Literal["x", "y", "both"] | Axis, optional
            The axis to move ("x", "y", or "both"), by default "x".
        position : int, optional
            The absolute position to move to, by default 0.
        wait : bool, optional
            If True, wait for finishing the move, by default True.
        """
        axis_int = axis_int = (
            Axis[axis.upper()].value if isinstance(axis, str) else axis.value
        )
        cmd = f"{group}A{axis_int}:{position}"
        self.sendtext(cmd)
        if wait:
            self.wait_during_move(group=group, printing=VERBOSE)

    def move_origin(
        self, group: Literal[1, 2] = 1, axis: Literal["x", "y", "both"] | Axis = "x"
    ) -> None:
        """Move the specified axis to the origin (home position).

        Parameters
        ----------
        group : Literal[1, 2], optional
            The group number (1 or 2), by default 1.
        axis : Literal["x", "y", "both"] | Axis, optional
            The axis to move to the origin ("x", "y", or "both"), by default "x".
        """
        axis_int = axis_int = (
            Axis[axis.upper()].value if isinstance(axis, str) else axis.value
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
        """Move to the relative position.

        Parameters
        ----------
        group : Literal[1, 2], optional
            The group number (1 or 2), by default 1.
        axis : Literal["x", "y", "both"] | Axis, optional
            The axis to move ("x", "y", or "both"), by default "x".
        move : int, optional
            The relative distance to move, by default 0.
        wait : bool, optional
            If True, wait for finishing the move, by default True.
        """
        axis_int = axis_int = (
            Axis[axis.upper()].value if isinstance(axis, str) else axis.value
        )
        cmd = f"{group}M{axis_int}:{move}"
        self.sendtext(cmd)
        if wait:
            self.wait_during_move(group=group, printing=VERBOSE)
