import socket


class TcpSocketWrapper(socket.socket):
    """Very thin wrapper of socket"""

    def __init__(self, verbose=False):
        self._verbose = verbose
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, bytes, flags=0):
        if self._verbose:
            print("WRITING:", bytes)
        super().send(bytes, flags)

    def recv(self, bufsize, flags=0):
        if self._verbose:
            print("READING: ", end="")
        msg = super().recv(bufsize, flags)
        if self._verbose:
            print(msg)
        return msg


class Picomotor8742:
    """Newport Picomotor 8742 (ethernet connection) class"""

    def __init__(
        self,
        ipaddr: str,
        port=23,
        naxis=4,
        timeout=2,
        name="Picomotor8742",
        verbose=False,
    ):
        self.name = name
        self.ipaddr = ipaddr
        self.port = port
        self.timeout = timeout
        self.naxis = naxis
        self.verbose = verbose
        self.sock = None

    def connect(self):
        """Connect the Picomotor device"""
        self.sock = TcpSocketWrapper(self.verbose)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.ipaddr, self.port))

    def cmd(self, axis, cmd, *args) -> None:
        """Send a command to 8742 controller

        Parameters
        ----------
        axis: int
            axis number (1-4)
        cmd: str
            command with argument (if required)
        """
        cmdstr = "{:d}{:s}".format(axis, cmd)
        cmdstr += ",".join(map(str, args)) + "\n"
        self.sock.send(cmdstr.encode("utf-8"))

    def ask(self, axis: int, cmd: str, *args) -> bytes:
        """"""
        self.cmd(axis, cmd, *args)
        ans = self.sock.recv(128)
        if ans[0] == 255:
            ans = self.sock.recv(128)
        assert ans[-2:] == b"\r\n"
        return ans.strip()

    def move_rel(self, axis: int = 1, distance: int = 0) -> None:
        """Move relatively

        Parameters
        ----------
        axis: int
            Axis number
        distance: int
            Relative distance (step)
        """
        self.cmd(axis, "PR{:d}".format(distance))

    def move_indefinitely(self, axis: int = 1, positive: bool = True) -> None:
        """Move indefinitely

        Need stop command to stop.

        Parameters
        ----------
        axis: int
            Axis number
        positive: bool
            if True move in positive direction
        """
        if positive:
            self.cmd(axis, "MV+")
        else:
            self.cmd(axis, "MV-")

    def position(self, axis: int = 1) -> int:
        """Return Axis position in step

        Parameters
        ----------
        axis: int
            The axis number  (1-4)

        Returns
        ----------
        int
            axis position in steps
        """
        return int(self.ask(axis, "TP?"))

    def stop(self, axis: int = 1) -> None:
        """Stop motion

        Parameters
        -----------
        axis: int
            Axis number
        """
        self.cmd(axis, "ST")

    def set_velocity(self, axis: int = 1, velocity: int = 2000) -> None:
        """Set velocity

        Parameters
        -----------
        axis: int
            Axis number
        velocity: int
            Velocity (steps/sec)  default is 2000
        """
        self.cmd(axis, "VA{:d}".format(int(velocity)))

    def set_acceleration(self, axis: int = 1, acceleration: int = 100000) -> None:
        """Set Acceleration

        Parameters
        -----------
        axis: int
            Axis number
        acceleration: int
            Acceleration (steps/sec^2)  default is 100000
        """
        self.cmd(axis, "AC{:d}".format(int(acceleration)))

    def motion_done_query(self, axis: int = 1) -> int:
        """Motion done status query

        Parameters
        -----------
        axis: int
            Axis number

        Returns
        -------
        int
            0 is in progress, 1 is not in progress
        """
        return int(self.ask(axis, "MD?"))

    def acceleration(self, axis: int = 1) -> int:
        """Return the acceleration

        Parameters
        ----------
        axis: int
            Axis number

        Returns
        -------
        int
        """
        return int(self.ask(axis, "AC?"))

    def velocity(self, axis: int = 1) -> int:
        """Return the velocity

        Parameters
        ----------
        axis: int
            Axis number

        Returns
        -------
        int
        """
        return int(self.ask(axis, "VA?"))
