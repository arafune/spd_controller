# -*- coding: utf-8 -*-

from __future__ import annotations

import threading
import time

import serial
from serial.tools import list_ports


class Comm:
    """
    Serial communicadtion  (Very thin wrapper of serial class)
    """

    def __init__(self, term: str = "\r") -> None:
        """Initialization

        Parameters
        ----------
        term : str, optional
            terminal character, by default "\r"
        """
        self.TERM: str = term
        self.is_portopen = False
        self.recvData = bytearray()
        self.event = threading.Event()

    def connect(self, serial_num: str) -> str | None:
        """Searches all serial ports for device with matching serial number (USB)

        Parameters
        ----------
        serial_num : str
            serial number

        Returns
        -------
        str
            port name
        """
        ports = list_ports.comports()
        for port in ports:
            try:
                if port.serial_number.startswith(serial_num):
                    return port.device
            except AttributeError:
                pass

    def recv(self, timeout: float = 3.0) -> tuple[bool, bytearray]:
        """Receive the data (within waiting time).

        Parameters
        ----------
        timeout : float, optional
            Time for the timeout, by default 3.0

        Returns
        -------
        tuple[bool, bytearray]

        """
        time_start = time.time()
        time_end = time_start
        self.event.clear()
        self.recvData.clear()
        result = False

        while not self.event.is_set():
            time_end = time.time()
            if time_end - time_start > timeout:
                result = False
                self.stop()
                print("timeout:{0}sec".format(timeout))
                break

            buff: bytes = self.comm.read()
            if len(buff) > 0:
                self.recvData.extend(buff)
                if (self.recvData.find(self.TERM.encode("utf-8"))) >= 0:
                    result = True
                    self.stop()
                    break
        return (result, self.recvData)

    def send(self, data: bytes) -> None:
        """Send the byte to the device

        Parameters
        ----------
        data : bytes
            Data to send
        """
        self.comm.write(data)

    def sendtext(self, text: str) -> None:
        """An syntax sugar of send.

        As the argument of send should be byte, which is annoying.

        Parameters
        ----------
        text : str
            Text string to send.
        """

        text = text + self.TERM
        self.comm.write(text.encode("utf-8"))

    def recvbytes(self) -> bytes:
        """Read the byte from the device.

        Returns
        -------
        bytes
            Byte string from the machine.
        """
        return self.comm.readline()

    def recvtext(self) -> str:
        """Read the text endwith the TERM (default: \r) from the device

        Returns
        --------
        str
        """
        return self.recvbytes().decode("utf-8")

    def stop(self) -> None:
        """Stop the data transfer"""
        self.event.set()

    def open(
        self,
        tty: str | None = None,
        baud: int = 9600,
        xonxoff: bool = False,
        rtscts: bool = False,
        port: str | None = None,
    ) -> bool:
        """Open the serial port

        Parameters
        ----------
        tty : str
            The port name ("/dev/ttyUSB0" for example)
        baud : int, optional
            baud rate, by default 9600
        xonxoff : bool, optional
            xon/xoff software flow control, by default False
        rtscts : bool, optional
            RTS/CTS hardware flow control, by default False
        port : str| None
            The port name  (Used for USB connection).


        Returns
        -------
        bool
            Return True if successfully connected.
        """
        try:
            if port:
                self.comm = serial.Serial(
                    baudrate=baud, xonxoff=xonxoff, timeout=1, rtscts=rtscts, port=port
                )
            else:
                self.comm = serial.Serial(
                    tty, baud, xonxoff=xonxoff, timeout=1, rtscts=rtscts
                )
            self.is_portopen = True
        except Exception:
            self.is_portopen = False

        return self.is_portopen

    def read(self, size: int = 1) -> bytes:
        """Read the byte characters from the machine.

        Parameters
        ----------
        size : int, optional
            the number of characters for read, by default 1

        Returns
        -------
        bytes
            The byte string from the machine.
        """
        return self.comm.read(size)

    def close(self) -> None:
        """Close the port, explicitly"""
        self.stop()
        if self.is_portopen:
            self.comm.close()
        self.is_portopen = False


if __name__ == "__main__":
    comm = Comm()
    comm.open("/dev/ttyUSB0", 57600, xonxoff=True)
    comm.send("*RST\r".encode("utf-8"))
    comm.send("*CLS\r".encode("utf-8"))
    comm.send("CONF:CURR\r".encode("utf-8"))
    """ # SENS:DATA を使う必要性はない
    comm.send("SENS:FUNC?\r".encode('utf-8'))
    result, data = comm.recv(10)
    print(result)
    print(data)

    comm.send("SENS:DATA?\r".encode('utf-8'))
    result, data = comm.recv(10)
    print(data)
    """
    comm.send("CURR:RANG 2.1e-5\r".encode("utf-8"))
    """comm.send('AVER oFF\r'.encode('utf-8'))
    comm.send('DISP:DIG 7\r'.encode('utf-8'))
    comm.send('FORM:ELEM READ\r'.encode('utf-8'))
    comm.send('DISP:ENAB OFF\r'.encode('utf-8'))
    comm.send('INIT\r'.encode('utf-8'))
    comm.send('READ?\r'.encode('utf-8'))
    """
    result, data = comm.recv(10)
    print(result)
    print(data)
    while True:
        comm.send("READ?\r".encode("utf-8"))
        result, data = comm.recv(10)
        print(data)
    comm.close()  # Actually, this line doesn't work.
