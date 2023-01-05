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
        self, ipaddr, port=23, naxis=4, timeout=2, name="Picomotor8742", verbose=False
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

    def cmd(self, axis, cmd, *args):
        """Send a command to 8742 controller

        Parameters
        ----------
        axis:

        cmd:


        """
        cmdstr = "%d%s" % (axis, cmd)
        cmdstr = ",".join(map(str, args)) + "\n"
        self.sock.send(cmdstr.encode())

    def ask(self, axis: int, cmd: str, *args):
        self.cmd(axis, cmd, *args)
        ans = self.sock.recv(128)
        if ans[0] == 255:
            ans = self.sock.recv(128)
        assert ans[-2:] == b"\r\n"
        return ans.strip()

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
        pass
