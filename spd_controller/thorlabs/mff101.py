#!/usr/bin/env python3
from __future__ import annotations

from . import THORLABS_MOTION_CONTROL


class MFF101(THORLABS_MOTION_CONTROL):
    """Thorlabs MFF101 Motor flipper controller class"""

    def __init__(self, serial_num: str | int) -> None:
        super().__init__(serial_num)

    def identify(self) -> None:
        """Identify itself by flashing the LED

        MGMSG_MODE_IDENTIFY
        """
        return self.write("230200005001")

    def position(self) -> int:
        """Return current position 1 or 2

        Returns
        ----------
        int
            the current position 1 or 2
        """
        self.write("290400005001")  # MGMSG_MOT_REQ_STATUSBITS
        return self.rd(12)[8]

    def move_forward(self) -> None:
        """Move flipper forward (2->1)

        MGMSG_MOT_MOVE_JOG   (64 04 (Chan Ident) Direction d s)
            * Chan Ident: The channel being acdressed
            * Direction : The direction to Jog.  Set this byte to 0x01 to jog forward, or to 0x02 to jog in the reverse diregtion.
        """
        return self.write("6A0401015001")

    def move_backward(self) -> None:
        """Move flipper backward  (1->2)

        MGMSG_MOT_MOVE_JOG   (64 04 (Chan Ident) Direction d s)
            * Chan Ident: The channel being acdressed
            * Direction : The direction to Jog.  Set this byte to 0x01 to jog forward, or to 0x02 to jog in the reverse diregtion.
        """
        return self.write("6A0401025001")

    def flip(self) -> None:
        """Flip the position"""
        if self.position() == 1:
            self.move_backward()
        else:
            self.move_forward()
