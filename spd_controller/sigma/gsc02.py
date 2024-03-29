#! /usr/bin/env python3
"""GSC-02 controller to control variable ND filter.

Hardware specification:

* Model name OSMS-60YAW (SIGMAKOKI Co., Ltd.)
* Motor Drive Cuurent: 0.75 (A)
* 144000 pulse : 360 degree
"""

from __future__ import annotations

import argparse

from serial.tools import list_ports

from .. import Comm


class GSC02(Comm):
    """Class for DSC-02 controller.

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
        if port:
            self.open(tty=port, baud=9600)
        else:
            ttys = [port.device for port in list_ports.comports()]
            for tty in ttys:
                self.open(tty=tty, baud=9600, rtscts=True)
                self.sendtext("?:V")
                return_info = self.recvtext().strip()
                if return_info == "V1.32":
                    self.is_portopen = True
                    self.close()
                    self.open(tty=tty, baud=9600, rtscts=True)
                    return
                self.close()
            msg = "Check the port. Cannot find the connection to the ND filter"
            raise RuntimeError(
                msg,
            )

    def angle(self) -> float:
        """Return the current angle of the rotation stage.

        Returns
        -------
        float
            The current angle of the stage
        """
        self.sendtext("Q:")
        reply: str = self.recvtext().strip().split(",")[0]
        return int(reply) * 0.0025

    def move_to_origin(self, axis: int = 1, wait: bool = True) -> None:
        """Go to mechanical origin.

        Parameters
        ----------
        wait : bool, optional
            If true show the current angle during rotation, by default True
        """
        self.sendtext(f"H:{axis}-")
        if wait:
            self.waiting_for_rotation()

    def move_rel(self, pulse: int, axis: int = 1, *, wait: bool = True) -> None:
        """Rotate the stage by the input value.

        Parameters
        ----------
        pulse : int
            The number of pulses.
        axis: int
            axis
        wait : bool, optional
            If true show the current angle during rotation, by default True
        """
        if pulse >= 0:
            command = f"M:{axis}+P{int(abs(pulse))}"
        else:
            command = f"M:{axis}-P{int(abs(pulse))}"
        self.sendtext(command)
        self.sendtext("G")
        if wait:
            self.waiting_for_rotation()

    def rotate(self, angle_deg: float, axis: int = 1, *, wait: bool = True) -> None:
        """Rotate the stage by the input angle.

        Parameters
        ----------
        angle_deg : float
            The angle to rotate
        axis: int
            axis number
        wait : bool, optional
            If true show the current angle during rotation, by default True
        """
        pulse = int(angle_deg / 0.0025)
        self.move_rel(pulse, axis=axis, wait=wait)

    def set_angle(self, angle_deg: float, axis: int = 1, *, wait: bool = True) -> None:
        """Set the angle of the ND filter.

        Parameters
        ----------
        angle_deg : float
            angle of the ND filter
        axis: int
            axis number
        wait : bool, optional
            If true show the current angle during rotation, by default True

        """
        current_angle = self.angle()
        rotate_angle = angle_deg - current_angle
        self.rotate(rotate_angle, axis=axis, wait=wait)

    def rotating(self) -> float | None:
        """Check the ND filter is rotating.

        Returns
        -------
        float|None
            The current angle, if motor is stopped return None.
        """
        self.sendtext("Q:")
        [position, _, _, _, status] = self.recvtext().strip().split(",")
        if status == "R":
            return None
        return int(position) * 0.0025

    def waiting_for_rotation(self) -> None:
        """Wait for the rotation."""
        current_angle = self.rotating()
        while current_angle:
            print(f"{current_angle:.4f}")
            current_angle = self.rotating()

    def force_stop(self, axis: int = 1) -> float:
        """Force stop motor.

        Returns
        -------
        float:
            The Current angle of the ND filter
        """
        self.sendtext(f"L:{axis}")
        return self.angle()

    def check_stop(self) -> bool:
        """Return True if the motor stops.

        Returns
        -------
        bool
            True if the motor stops.
        """
        self.sendtext("!:")
        tmp = self.recvtext().strip()
        if tmp == "R":
            return True
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("angle", metavar="Angle", type=float)
    args = parser.parse_args()
    g = GSC02()
    g.set_angle(args.angle, wait=False)
