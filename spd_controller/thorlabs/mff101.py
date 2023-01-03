#!/usr/bin/env python3

from . import THORLABS_MOTION_CONTROL


class MFF101(THORLABS_MOTION_CONTROL):
    """Thorlabs MFF101 Motor flipper controller class"""

    def __init__(self, serial_num) -> None:
        super().__init__(serial_num)

    def identify(self) -> None:
        """Identify itself by flashing the LED"""
        return self.write("230200005001")  # MGMSG_MODE_IDENTIFY

    def position(self) -> int:
        """Return current position 1 or 2

        Returns
        ----------
        int
            the current position 1 or 2
        """
        self.write("290400005001")  # MGMSG_MOT_REQ_STATUSBITS
        return self.rd(12)[8]

    def forward_move(self) -> None:
        """Move flipper forward (2->1)

        64 043 (Chan Ident) Direction d s
        Chan Ident: The channel being acdressed
        Direction : The direction to Jog.  Set this byte to 0x01 to jog forward, or to 0x02 to jog in the reverse diregtion.
        """
        return self.write("6A0401015001")  # MGMSG_MOT_MOVE_JOG

    def backward_move(self) -> None:
        """Move flipper backward  (1->2)

        64 043 (Chan Ident) Direction d s
        Chan Ident: The channel being acdressed
        Direction : The direction to Jog.  Set this byte to 0x01 to jog forward, or to 0x02 to jog in the reverse diregtion.
        """
        return self.write("6A0401025001")  # MGMSG_MOT_MOVE_JOG

    def flip(self) -> None:
        """Flip the position"""
        if self.position() == 1:
            self.backward_move()
        else:
            self.forward_move()
