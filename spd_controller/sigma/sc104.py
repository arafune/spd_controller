#!/usr/bin/python3
"""SIGMA TECH SC104

9600 bps
CR+LF
8bit
stop bit 1bit
No parity

* Repeat accuracy : < 0.2 micron
* Minimum resolution: 0.1 micron
"""

from __future__ import annotations

import argparse

from serial.tools import list_ports

from .. import Comm


class SC104(Comm):
    """Class for SC-104 Linear translation stage controller"""

    def __init__(self, term: str = "\r\n") -> None:
        """
        [TODO:summary]

        [TODO:description]

        Parameters
        ----------
        term
            [TODO:description]

        Returns
        -------
        None
            [TODO:description]

        Raises
        ------
        RuntimeError:
            [TODO:description]
        """
        super().__init__(term=term)
        ttys = [port.device for port in list_ports.comports()]
        for tty in ttys:
            self.open(tty=tty, baud=9600)
            self.sendtext("MODE?")
            return_info: str = self.recvtext().strip()
            if return_info == "LOCAL":
                self.sendtext("MODE:REMOTE")
            self.sendtext("MODE?")
            return_info = self.recvtext().strip()
            if return_info == "REMOTE":
                self.is_portopen = True
                self.close()
                self.open(tty=tty, baud=9600, xonxoff=True)
                return None
            else:
                self.close()
        raise RuntimeError(
            "Check the port. Cannot find the connection to the ND filter"
        )

    def position(self) -> float:
        """Return the current postion.

        Returns
        -------
        float
            The current position in mm unit.
        """

        self.sendtext("P:1")
        pos = int(self.recvtext().strip())
        pos_mm = pos * 1e-4
        return pos_mm

    def move_to_origin(self, wait: bool = True) -> None:
        """Move to the mechanical origin.

        And electric zero is set at this point.
        """
        self.sendtext("H:1")
        if wait:
            self.wait_during_move()

    def move_to_zero(self, wait: bool = True) -> None:
        """Move to electrical origin which can be varied.

        Parameters
        ----------
        wait : bool
            If true show the current position during move, by default True
        """
        self.sendtext("Z:1")
        if wait:
            self.wait_during_move()

    def set_zero(self) -> None:
        """Set the current position as the electrical origin."""
        self.sendtext("R:1")

    def move_abs(self, pos: float, wait: bool = True, micron: bool = False) -> None:
        """Move to the absolute position.

        Parameters
        -----------
        pos: float
            position. Default unit is mm.
        micron: Boolean
            if True, the unit of position is micron (default: False)
        wait : bool, optional
            If true show the current position during move, by default True
        """
        if micron:
            pos /= 1000
        if pos >= 0:
            command = "A:1+P{}".format(int(abs(pos * 1e4)))
        else:
            command = "A:1-P{}".format(int(abs(pos * 1e4)))
        self.sendtext(command)
        self.sendtext("G")
        if wait:
            self.wait_during_move()

    def move_rel(self, move: float, wait: bool = True, micron: bool = False) -> None:
        """Move by the value from the current position(Relative move).

        Parameters
        -----------
        move: float
            position. Default unit is mm.
        micron: bool
            if True, the unit of position is micron (default: False)
        wait : bool, optional
            If true show the current position during move, by default True
        """

        if micron:
            move /= 1000
        if move >= 0:
            command = "M:1+P{}".format(int(abs(move * 1e4)))
        else:
            command = "M:1-P{}".format(int(abs(move * 1e4)))
        self.sendtext(command)
        self.sendtext("G")
        if wait:
            self.wait_during_move()

    def moving(self) -> float | None:
        """Check the current stage condition.

        Returns
        ---------
        float
            the current position, if the stage is not moving, return None
        """
        self.sendtext("Q:")
        tmp = self.recvtext().split(",")
        if tmp[3] == "K":
            return None
        else:
            return int(tmp[0]) * 1.0e-4

    def set_speed(self, speed: float) -> None:
        """Set stage spped in mm/s unit

        Parameters
        ----------
        speed : float
            Speed of the stage mm/s
        """
        assert speed > 0
        command: str = "D:1F{}".format(int(speed * 1e4))
        self.sendtext(command)
        return None

    def set_acceralation_time(self, acc: int) -> None:
        """Set accelaration/deceleration time  (default 100ms)

        Parameters
        ----------
        acc: int
            Accelaration/deceleration time in ms unit.
        """
        assert acc > 0
        command: str = "ACC: 1 {}".format(acc)
        self.sendtext(command)
        return None

    def wait_during_move(self) -> None:
        """Wait and print the current position during the move"""
        current_position: float | None = self.moving()
        while current_position:
            print("{:.4f}".format(current_position))
            current_position = self.moving()

    def force_stop(self) -> float:
        """Force stop the motor

        Returns
        -------
        float
            The stop position of the mirrors
        """
        self.sendtext("L:1")
        return self.position()

    def check_stop(self) -> bool:
        """Return True if the motor stops (Not-busy)

        Returns
        -----------
        bool
            True if the motor stops.
        """
        self.sendtext("SRQ:")
        tmp = self.recvtext().split(",")
        if tmp[1] == "K":
            return True
        return False

    def back_and_forth(
        self, position_a: float, position_b: float, wait: bool = True
    ) -> None:
        """Reciprocate the stage between postion A and B.


        Parameters
        ----------
        position_a : float
            position A in mm unit.
        position_b : float
            position B in mm unit.
        wait : bool, optional
            If true show the current position during move, by default True
        """
        while True:
            try:
                self.move_abs(position_a, wait=wait)
                self.move_abs(position_b, wait=wait)
            except KeyboardInterrupt:
                self.recvbytes()
                break

    def goto_overlap(self) -> None:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    # parser.add_argument("--tty", metavar="tty_name", type=str, default="/dev/ttyUSB1")
    parser.add_argument("position", metavar="Postion", type=float)
    args = parser.parse_args()
    s = SC104()
    s.move_abs(args.position, wait=False)
