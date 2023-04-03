#! /usr/bin/env python3
"""GSC-02 controller

To control variable ND filter.

To work Motorized ND Filter Holder.

Hard ware side information:
    * Model name OSMS-60YAW (SIGMAKOKI Co., Ltd.)
    * Motor Drive Cuurent: 0.75 (A)
    * 144000 pulse : 360 degree
"""

from __future__ import annotations

import argparse

from serial.tools import list_ports

from .. import Comm


class GSC02(Comm):
    """Class for DSC-02 controller"""

    def __init__(self, term: str = "\r\n", port: str = "") -> None:
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
                    return None
                else:
                    self.close()
            raise RuntimeError(
                "Check the port. Cannot find the connection to the ND filter"
            )

    def move_mechanical_zero(self, axis: int = 1, wait: bool = True) -> None:
        """Go to "mechanical zero" position.

        Parameters
        ----------
        wait : bool, optional
            If true show the current angle during rotation, by default True
        """
        self.sendtext("H:{}-".format(axis))
        if wait:
            self.waiting_for_rotation()

    def move_to_rel(self, pulse: int, axis: int = 1, wait: bool = True) -> None:
        """Rotate the stage by the input value

        Parameters
        ----------
        pulse : int
            The number of pulses.
        wait : bool, optional
            If true show the current angle during rotation, by default True
        """
        if pulse >= 0:
            command = "M:{}+P{}".format(axis, int(abs(pulse)))
        else:
            command = "M:{}-P{}".format(axis, int(abs(pulse)))
        self.sendtext(command)
        # time.sleep(0.03)  # 0.01 だと動かない。 RTS/CTS flow をオンにしたらいらない?
        self.sendtext("G")
        if wait:
            self.waiting_for_rotation()

    def rotate(self, angle_deg: float, axis: int = 1, wait: bool = True) -> None:
        """Rotate the stage by the input angle

        Parameters
        ----------
        angle_deg : float
            The angle to rotate
        wait : bool, optional
            If true show the current angle during rotation, by default True
        """

        pulse = int(angle_deg / 0.0025)
        self.move_to_rel(pulse, axis=axis, wait=wait)

    def set_angle(self, angle_deg: float, axis: int = 1, wait: bool = True) -> None:
        """Set the angle of the ND filter

        Parameters
        ----------
        angle_deg : float
            angle of the ND filter
        wait : bool, optional
            If true show the current angle during rotation, by default True

        """
        current_angle = self.angle()
        rotate_angle = angle_deg - current_angle
        self.rotate(rotate_angle, axis=axis, wait=wait)

    def angle(self) -> float:
        """Return the current angle of the rotation stage

        Returns
        -------
        float
            The current angle of the stage
        """
        self.sendtext("Q:")
        reply: str = self.recvtext().strip().split(",")[0]
        return int(reply) * 0.0025

    def rotating(self) -> float | None:
        """Check the ND filter is rotating

        Returns
        -------
        float|None
            The current angle, if motor is stopped return None.
        """

        self.sendtext("Q:")
        [position, _, _, _, status] = self.recvtext().strip().split(",")
        if status == "R":
            return None
        else:
            return int(position) * 0.0025

    def waiting_for_rotation(self) -> None:
        """Wait for the rotation"""
        current_angle = self.rotating()
        while current_angle:
            print("{:.4f}".format(current_angle))
            current_angle = self.rotating()

    def force_stop(self, axis: int = 1) -> float:
        """Force stop motor

        Returns
        -------
        float:
            The Current angle of the ND filter
        """
        self.sendtext("L:{}".format(axis))
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
