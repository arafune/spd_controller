from __future__ import annotations

import binascii

import serial
from serial.tools import list_ports

__all__: list[str] = ["k10cr1", "mff101"]
__version__: str = "0.1.0"


class THORLABS_MOTION_CONTROL:
    """An abstract layer for Thorlabs Motion Control"""

    def __init__(self, serial_num: str | int) -> None:
        """Set-up and connect to device with serial number

        Parameters
        ---------------
        serial_num: str| int
            serial number of the MFF101
        """
        self.serial_num = str(serial_num)
        self.ready = False
        self.connect()
        if not self.ready:
            print(
                "Unable to connect to device with serial number: {}".format(serial_num)
            )
        else:
            print(
                "Connect successful to device with serial number: {}".format(serial_num)
            )

    def connect(self) -> None:
        """Searhes all com ports for device with matching serial number and opens a connection"""
        ports = list_ports.comports()
        for port in ports:
            try:
                if port.serial_number.startswith(self.serial_num):
                    self.ser = serial.Serial(
                        baudrate=115200, timeout=0.1, port=port.device
                    )
                    self.ready = True
                    break
            except AttributeError:
                pass

    def rd(self, bytelen: int) -> bytes:
        """Read buffer

        Parameters
        ---------------
        bytelen: int
            length of byte to read

        Returns
        ---------
        bytes
        """
        x = self.ser.readline()
        while len(x) < bytelen:
            x = x + self.ser.readline()
        return x

    def write(self, x: str) -> int | None:
        """Write buffer

        Parameters
        -----------
        x: str
            String to buffer
        """
        command = bytearray.fromhex(x)
        return self.ser.write(command)


def decimal_to_hex(x: int, byte_length: int) -> str:
    """Generate hex string from integer

    After python3.2 to_byte method has been prepared.

    Parameters
    ----------
    x : int
        _description_
    byte_length : int
        _description_

    Returns
    -------
    str
        _description_
    """
    tmp = x.to_bytes(byte_length, byteorder="little", signed=True)
    return str(binascii.b2a_hex(tmp), encoding="utf-8")


def bytes_to_decimal(x: bytes) -> int:
    """Return the int from the bytes.   Essentially btd return the same value

    Parameters
    ----------
    x : bytes
        Represents an integer

    Returns
    -------
    int
        integer
    """
    return int.from_bytes(x, byteorder="little", signed=True)


"""
The source and destination fields require some further explanation.
In general, as the name suggests, they are used to indicate the
source and destination of the message. In non-card- slot type of
systems the source and destination of messages is always unambiguous,
as each module appears as a separate USB node in the system.
In these systems, when the host sends a message to the module,
it uses the source identification byte of 0x01 (meaning host)
and the destination byte of 0x50 (meaning “generic USB unit”).
(In messages that the module sends back to the host,
the content of the source and destination bytes is swapped.)
"""

"""なので、最後が 01 で終わるのは当然"""
