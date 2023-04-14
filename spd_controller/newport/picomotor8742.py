from typing_extensions import Literal

from .. import TcpSocketWrapper

Axis = Literal[1, 2, 3, 4]


class Picomotor8742:
    """Newport Picomotor 8742 (ethernet connection) class"""

    def __init__(
        self,
        host: str = "144.213.126.101",
        port: int = 23,
        naxis: int = 4,
        timeout: int = 2,
        name: str = "Picomotor8742",
        verbose: bool = False,
    ):
        self.name = name
        self.host = host
        self.port = port
        self.timeout = timeout
        self.naxis = naxis
        self.verbose = verbose
        self.sock = None

    def connect(self):
        """Connect the Picomotor device"""
        self.sock = TcpSocketWrapper(term="\n", verbose=self.verbose)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

    def cmd(self, axis: int, cmd: str, *args) -> int:
        """Send a command to 8742 controller

        Parameters
        ----------
        axis: Axis
            axis number (1-4)
        cmd: str
            command with argument (if required)
        """
        cmdstr = "{:d}{:s}".format(axis, cmd)
        cmdstr += ",".join(map(str, args)) + "\n"
        return self.sock.send(cmdstr.encode("utf-8"))

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
        try:
            self.cmd(axis, "PR{:d}".format(distance))
        except TypeError:
            pass

    def move_indefinitely(self, axis: Axis = 1, positive: bool = True) -> None:
        """Move indefinitely

        Need stop command to stop.

        Parameters
        ----------
        axis: Axis
            Axis number
        positive: bool
            if True move in positive direction
        """
        if positive:
            self.cmd(axis, "MV+")
        else:
            self.cmd(axis, "MV-")

    def position(self, axis: Axis = 1) -> int:
        """Return Axis position in step

        Parameters
        ----------
        axis: Axis
            The axis number  (1-4)

        Returns
        ----------
        int
            axis position in steps
        """
        return int(self.ask(axis, "TP?"))

    def force_stop(self, axis: Axis = 1) -> None:
        """Force stop the actuator.

        Parameters
        -----------
        axis: Axis
            Axis number
        """
        self.cmd(axis, "ST")

    def set_velocity(self, axis: Axis = 1, velocity: int = 2000) -> None:
        """Set velocity

        Parameters
        -----------
        axis: Axis
            Axis number
        velocity: int
            Velocity (steps/sec)  default is 2000
        """
        if velocity > 2000:
            print("The velocity should be less than 2000")
            return None
        self.cmd(axis, "VA{:d}".format(int(velocity)))

    def set_acceleration(self, axis: Axis = 1, acceleration: int = 100000) -> None:
        """Set Acceleration

        Parameters
        -----------
        axis: Axis
            Axis number
        acceleration: int
            Acceleration (steps/sec^2)  default is 100000
        """
        self.cmd(axis, "AC{:d}".format(int(acceleration)))

    def check_stop(self, axis: Axis = 1) -> bool:
        """Return True if the actuator is stop.

        Parameters
        -----------
        axis: Axis
            Axis number

        Returns
        -------
        bool
            True if the actuator is stop (not work)
        """
        if int(self.ask(axis, "MD?")):
            return True
        return False

    def acceleration(self, axis: Axis = 1) -> int:
        """Return the acceleration

        Parameters
        ----------
        axis: Axis
            Axis number

        Returns
        -------
        int
            acceleration value (step/sec^2)
        """
        return int(self.ask(axis, "AC?"))

    def velocity(self, axis: Axis = 1) -> int:
        """Return the velocity

        Parameters
        ----------
        axis: Axis
            Axis number

        Returns
        -------
        int
            velocity value (step/sec)
        """
        return int(self.ask(axis, "VA?"))

    def speed(self, axis: Axis = 1) -> int:
        """Alias of self.velocity

        Parameters
        --------------
        axis: Axis
            Axis number

        Returns
        ----------
        int:
            Speed (steps/sec)
        """
        return self.velocity(axis)

    def set_speed(self, axis: Axis, speed: int):
        """Alias of self.set_velocity

        Parameters
        ----------
        axis: Axis
            Axis number
        speed: int
            Speed to set (steps/sec)
        """
        self.set_velocity(axis, speed)
