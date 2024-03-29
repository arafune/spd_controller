from __future__ import annotations

import socket
import threading
import time

from typing import Literal

import serial
from serial.tools import list_ports


class SerialWrapper(serial.Serial):
    """Thin wrapper of serial.Serial.

    Attribute
    ---------
    """

    def __init__(self, term: str = "\n", *, verbose: bool = False) -> None:
        """Initialize."""
        self._verbose = verbose
        self.TERM = term

    def send(self, bytes_: bytes) -> int:
        return super().write(bytes_)

    def sendtext(self, text: str) -> int:
        text = text + self.TERM
        return self.send(text.encode("utf-8"))

    def recvbytes(self) -> bytes:
        return super().readline()

    def recvtext(self) -> str:
        return self.recvbytes().decode("utf-8")


class Comm:
    """Serial communicadtion  (Very thin wrapper of serial class)."""

    def __init__(self, term: str = "\r") -> None:
        r"""Initialize.

        Parameters
        ----------
        term : str, optional
            terminal character, by default "\r"
        """
        self.TERM: str = term
        self.is_portopen = False
        self.recvData = bytearray()
        self.event = threading.Event()

    def connect_usb(self, serial_num: str) -> str | None:
        """Alias of connect."""
        return self.connect(serial_num)

    def connect(self, serial_num: str) -> str | None:
        """Search all serial ports for device with matching serial number (USB).

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
            if isinstance(port.serial_number, str) and port.serial_number.startswith(
                serial_num
            ):
                return port.device
        return None

    def open_socket(
        self,
        address_port: tuple[str, int],
        timeout: float = 1,
        baud: int = 115200,
    ) -> bool:
        """Open socket through pyserial url_uandler"""
        socket_ = f"socket://{address_port[0]}:{address_port[1]}"
        self.comm = serial.serial_for_url(socket_)
        self.comm.timeout = timeout
        self.comm.baudrate = baud
        self.is_portopen = self.comm.is_open
        return self.comm.is_open

    def recv(self, timeout: float = 3.0) -> tuple[bool, bytearray]:
        """Receive the data (within waiting time).

        Parameters
        ----------
        timeout : float, optional
            Time for the timeout, by default 3.0

        Returns
        -------
        tuple[bool, bytearray]
           True in the first item if the received appropriately.
           The bytearray is the byte returned.
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
                print(f"timeout:{timeout}sec")
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
        """Send the byte to the device.

        Parameters
        ----------
        data : bytes
            Data to send
        """
        self.comm.write(data)

    def sendtext(self, text: str) -> None:
        """Syntax sugar of send.

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
        r"""Read the text endwith the TERM (default: \\r) from the device.

        Returns
        -------
        str
            returned text
        """
        return self.recvbytes().decode("utf-8")

    def stop(self) -> None:
        """Stop the data transfer."""
        self.event.set()

    def open(
        self,
        tty: str | None = None,
        baud: int = 9600,
        xonxoff: bool = False,
        rtscts: bool = False,
        port: str | None = None,
    ) -> bool:
        """Open the serial port.

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
                    baudrate=baud,
                    xonxoff=xonxoff,
                    timeout=1,
                    rtscts=rtscts,
                    port=port,
                )
            else:
                self.comm = serial.Serial(
                    tty,
                    baud,
                    xonxoff=xonxoff,
                    timeout=1,
                    rtscts=rtscts,
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
        """Close the port, explicitly."""
        self.stop()
        if self.is_portopen:
            self.comm.close()
        self.is_portopen = False


class TcpSocketWrapper(socket.socket):
    """Very thin wrapper of socket."""

    def __init__(
        self,
        term: Literal["\n", "\r\n", "\r"] = "\n",
        verbose: bool = False,
    ) -> None:
        self._verbose = verbose
        self.TERM = term
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, bytes: bytes, flags: int = 0) -> int:
        if self._verbose:
            print("WRITING:", bytes)
        return super().send(bytes, flags)

    def recv(self, bufsize: int, flags: int = 0) -> bytes:
        if self._verbose:
            print("READING: ", end="")
        msg = super().recv(bufsize, flags)
        if self._verbose:
            print(msg)
        return msg

    def sendtext(self, text: str) -> int:
        text = text + self.TERM
        return self.send(text.encode("utf-8"))

    def recvtext(self, byte_size: int) -> str:
        """"""
        return self.recv(byte_size).decode("utf-8")


class SocketClient:
    """Tiny Socket client.

    **This is obsolute class. Keep it just for the compatibility.
    Do not use for making a new class**

    """

    def __init__(self, host: str, port: int, term: str = "\n") -> None:
        self.host = host
        self.port = port
        self.TERM = term
        self.socket = None

    def sendtext(self, text: str) -> int:
        """An syntax suger of sendtext.

        To send the command to Remote_In Prodigy, the text is converted to byte with
        linefeed character self.

        Parameters
        ----------
        text: str
            input text

        Returns
        -------
        int: number of byte send
        """
        text = text + self.TERM
        return self.socket.send(text.encode("utf-8"))

    def recvtext(self, byte_size: int) -> str:
        """"""
        return self.socket.recv(byte_size).decode("utf-8")

    def send_recv(self, input_data: str) -> str:
        DATASIZE = 512  # 受信データバイト数
        # sockインスタンスを生成
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # ソケットをオープンにして、サーバーに接続
            sock.connect((self.host, self.port))
            # 入力データをサーバーへ送信
            sock.send(input_data.encode("utf-8"))
            # サーバーからのデータを受信
            rcv_data: bytes = sock.recv(DATASIZE)
            return rcv_data.decode("utf-8")
