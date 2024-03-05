from __future__ import annotations
import contextlib
from typing import Literal

from .. import TcpSocketWrapper
from random import random

Axis = Literal[1, 2, 3, 4]


class MockPicomoter8742:
    """Mock of Picomotor8742"""

    def __init__(self) -> None:
        pass

    def move_indefinitely(self, axis: Axis = 1, *, positive: bool = True) -> None:
        if positive:
            print(f"move positively about axis {axis}.")
        else:
            print(f"move negatively about axis {axis}.")

    def position(self, axis: Axis = 1) -> int:
        assert isinstance(axis, int)
        return int(random() * 1000)

    def force_stop(self, axis: Axis = 1) -> None:
        print(f"force_stop axis {axis}.")

    def set_velocity(self, axis: Axis = 1, velocity: int = 2000) -> None:
        print(f"velocity of axis {axis} is set at {velocity}.")

    def move_rel(self, axis: int, distance: int) -> None:
        print(f"move_rel: Axis {axis}, distance {distance}")

    def connect(self) -> None:
        pass


class Picomotor8742:
    """Newport Picomotor 8742 (ethernet connection) class."""

    def __init__(
        self,
        host: str = "144.213.126.101",
        port: int = 23,
        naxis: int = 4,
        timeout: int = 2,
        name: str = "Picomotor8742",
        *,
        verbose: bool = False,
    ) -> None:
        self.name = name
        self.host = host
        self.port = port
        self.timeout = timeout
        self.naxis = naxis
        self.verbose = verbose
        self.sock: TcpSocketWrapper | None = None

    def connect(self) -> None:
        """Connect the 8742 Picomotor device."""
        self.sock = TcpSocketWrapper(term="\n", verbose=self.verbose)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

    def cmd(self, axis: int, cmd: str, *args: str | bytes) -> int:
        """Send a command to 8742 controller.

        Parameters
        ----------
        axis: Axis
            axis number (1-4)
        cmd: str
            command with argument (if required)
        """
        cmdstr = f"{axis:d}{cmd:s}"
        cmdstr += ",".join(map(str, args)) + "\n"
        assert self.sock is not None
        return self.sock.send(cmdstr.encode("utf-8"))

    def ask(self, axis: int, cmd: str, *args: str | bytes) -> bytes:
        """"""
        self.cmd(axis, cmd, *args)
        assert self.sock is not None
        answer = self.sock.recv(128)
        if answer[0] == 255:
            answer = self.sock.recv(128)
        assert answer[-2:] == b"\r\n"
        return answer.strip()

    def move_rel(self, axis: int = 1, distance: int = 0) -> None:
        """Move relatively.

        Parameters
        ----------
        axis: int
            Axis number
        distance: int
            Relative distance (step)
        """
        with contextlib.suppress(TypeError):
            self.cmd(axis, f"PR{distance:d}")

    def move_indefinitely(self, axis: Axis = 1, *, positive: bool = True) -> None:
        """Move indefinitely.

        Need stop command to stop.

        Parameters
        ----------
        axis: Axis
            Axis number
        positive: bool
            if True move in positive direction
        """
        if positive:
            self.cmd(axis, "MV+")
        else:
            self.cmd(axis, "MV-")

    def position(self, axis: Axis = 1) -> int:
        """Return Axis position in step.

        Parameters
        ----------
        axis: Axis
            The axis number  (1-4)

        Returns
        -------
        int
            axis position in steps
        """
        return int(self.ask(axis, "TP?"))

    def force_stop(self, axis: Axis = 1) -> None:
        """Force stop the actuator.

        Parameters
        ----------
        axis: Axis
            Axis number
        """
        self.cmd(axis, "ST")

    def set_velocity(self, axis: Axis = 1, velocity: int = 2000) -> None:
        """Set velocity.

        Parameters
        ----------
        axis: Axis
            Axis number
        velocity: int
            Velocity (steps/sec)  default is 2000
        """
        if velocity > 2000:
            print("The velocity should be less than 2000")
            return
        self.cmd(axis, f"VA{int(velocity):d}")

    def set_acceleration(self, axis: Axis = 1, acceleration: int = 100000) -> None:
        """Set Acceleration.

        Parameters
        ----------
        axis: Axis
            Axis number
        acceleration: int
            Acceleration (steps/sec^2)  default is 100000
        """
        self.cmd(axis, f"AC{int(acceleration):d}")

    def check_stop(self, axis: Axis = 1) -> bool:
        """Return True if the actuator is stop.

        Parameters
        ----------
        axis: Axis
            Axis number

        Returns
        -------
        bool
            True if the actuator is stop (not work)
        """
        if int(self.ask(axis, "MD?")):
            return True
        return False

    def acceleration(self, axis: Axis = 1) -> int:
        """Return the acceleration.

        Parameters
        ----------
        axis: Axis
            Axis number

        Returns
        -------
        int
            acceleration value (step/sec^2)
        """
        return int(self.ask(axis, "AC?"))

    def velocity(self, axis: Axis = 1) -> int:
        """Return the velocity.

        Parameters
        ----------
        axis: Axis
            Axis number

        Returns
        -------
        int
            velocity value (step/sec)
        """
        return int(self.ask(axis, "VA?"))

    def speed(self, axis: Axis = 1) -> int:
        """Alias of self.velocity.

        Parameters
        ----------
        axis: Axis
            Axis number

        Returns
        -------
        int:
            Speed (steps/sec)
        """
        return self.velocity(axis)

    def set_speed(self, axis: Axis, speed: int) -> None:
        """Alias of self.set_velocity.

        Parameters
        ----------
        axis: Axis
            Axis number
        speed: int
            Speed to set (steps/sec)
        """
        self.set_velocity(axis, speed)
