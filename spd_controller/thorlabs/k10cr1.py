from __future__ import annotations

from . import THORLABS_MOTION_CONTROL, bytes_to_decimal, decimal_to_hex


class K10CR1(THORLABS_MOTION_CONTROL):
    """Thorlabs K10CR1 rotation stage class."""

    def __init__(self, serial_num: str | int) -> None:
        super().__init__(serial_num)

    def angle_to_DU(self, ang: float) -> int:
        return int(ang * 24576000 / 180)

    def DU_to_angle(self, DU: int) -> float:
        return DU * 180 / 24576000

    def identify(self) -> int | None:
        """Identify itself by flashing its front panel LEDs"""
        return self.write("230200005001")  # 23, 02, 00, 00, 50, 01

    def set_home_speed(self, speed_deg_s: float) -> None:
        """Set the velocity for homing

        Parameters
        ----------
        speed_deg_s : int
            rotation speed in degree/s.
        """
        set_home_params: str = "40040E00d001"
        channel: str = "0100"
        home_direction: str = "0200"
        limit_switch: str = "0100"
        velocity: str = decimal_to_hex(int(7329109 * speed_deg_s), 4)
        offset_distance: str = decimal_to_hex(self.angle_to_DU(0), 4)
        self.write(
            set_home_params
            + channel
            + home_direction
            + limit_switch
            + velocity
            + offset_distance
        )
        return None

    def home(self) -> bytes:
        """Start to a home position.

        MGMSG_MOT_MOVE_HOME
        """
        self.set_home_speed(10)
        self.write("430401005001")  # 43, 04, 01, 00, 50, 01
        return self.rd(6)

    def move_rel(self, angle_deg: float) -> None:
        """Start a relative move.

        The longer version (6 byte header plus 6 data bytes) is used.
        Thus, the third and 4th bytes is "06 00"

        Parameters
        -----------
        angle_deg: float
            Relative rotation angle in degree.
        """
        rel_position: str = decimal_to_hex(self.angle_to_DU(angle_deg), 4)
        channel: str = "0100"
        header = "48040600d001"  # 48, 04, 06, 00, d0, 01
        cmd: str = header + channel + rel_position
        self.write(cmd)

    def move_abs(self, angle_deg: float) -> None:
        """Start a absolute move.

        Parameters
        ----------
        angle_deg : float
            Absolute angle of the stage head in degree.
        """
        abs_position: str = decimal_to_hex(self.angle_to_DU(angle_deg), 4)
        channel: str = "0100"
        header: str = "53040600d001"  # 53, 04, 06, 00, d0, 01
        cmd: str = header + channel + abs_position
        self.write(cmd)
        # return self.rd(20)

    def zerobacklash(self) -> None:
        backlash_position = decimal_to_hex(self.angle_to_DU(0), 4)
        channel: str = "0100"
        header: str = "3A040600d001"  # 3A, 04, 06, 00, d0, 01
        cmd: str = header + channel + backlash_position
        self.write(cmd)

    def jog(self) -> bytes:
        """Jog starts

        Returns
        -------
        Start a jog move
        """
        self.write("6a0401015001")  # 6a, 04, 01, 01, 50, 01
        # the first 01 is the channel.
        # the second 01 is the forward jog.
        return self.rd(20)

    def getpos(self) -> float:
        """Return the current angle.

        Returns
        --------------
        float
            The current angle (degree)
        """
        self.write("110401005001")  # 11, 04, 01, 00, 50, 01
        bytedata: bytes = self.rd(12)[8:]
        x = self.DU_to_angle(bytes_to_decimal(bytedata))
        return float("%.3f" % x)
