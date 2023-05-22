#!/usr/bin/env python

"""Class for Prodigy remote_in"""

from time import sleep

import numpy as np

from spd_controller.Specs.convert import Measure_type, itx

from .. import TcpSocketWrapper

BUFSIZE = 1024


class RemoteIn:
    r"""

    parameters
    ----------
    host: str
        hostname or IP address, default "144.213.126.146"

    port: int
        port number of for socket

    term: str
        line termination character, default is "\n"

    verbose: bool
        if True, verbose mode
    """

    def __init__(
        self,
        host: str = "144.213.126.140",
        port: int = 7010,
        term: str = "\n",
        verbose: bool = False,
    ) -> None:
        self.name: str = "Prodigy"
        self.host: str = host
        self.port: int = port
        self.TERM: str = term
        self.timeout = 2
        self.verbose: bool = verbose
        self.id: int = 1
        self.samples: int = 0
        # self.param: ProdigyParameter = {"Samples": 1, "DwellTime": 0.1}
        self.param: dict[str, str | float | int]
        self.data: list[float] = []

    def connect(self) -> str:
        r"""Open connection to SpecsLab Prodigy

        Returns
        --------
        str:
            Responce of "Connect command"

        Example
        -------
        '!0001 OK: ServerName:"SpecsLab Prodigy 4.86.2-r103043 " ProtocolVersion:1.18\n'
        """
        self.sock = TcpSocketWrapper(term=self.TERM, verbose=self.verbose)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))
        return self.sendcommand("Connect")

    def sendcommand(self, text: str, buffsize: int = BUFSIZE) -> str:
        r"""Send request command

        Request command syntax is as follows:
        ?<id> Command [InParams]

        where:

        * id: Unique request identifier (hexadecimal value, always 4 digits)
        * Command: Command name (character token, camel case, commands with
          spaces must be enclosed in double quotes)
        * InParams: Optional list of input parameters (“key:value”-list, space separated),
          specific for each command; the order of parameters is arbitrary.

        Each command and response are terminated by a newline character “\n”.

        Parameters
        ----------
        text: str
            Text as command to send Prodigy
        buffsize: int, optional
            buffer size  (default: BUFSIZE=1024)
        """
        request_str: str = "?" + format(self.id, "04X") + " " + text
        self.id += 1
        self.sock.sendtext(request_str)
        return self.sock.recvtext(buffsize)

    def disconnect(self) -> str:
        r"""Close connection to SpecsLab Prodigy

        Returns
        --------
        str:
            Responce of "Disconnect command" (Ex. '!0005 OK\n')
        """
        return self.sendcommand("Disconnect")

    def defineFAT(
        self,
        start_energy: float,
        end_energy: float,
        step: float,
        dwell: float = 0.096,
        pass_energy: float = 5,
        lens: str = "WideAngleMode",
        scanrange: str = "40V",
        with_check: bool = True,
    ) -> str:
        """Set measurment parameters of Phoibos (FAT mode)

        Send FAT spectrum specification for subsequent acquisition.
        Existing data must be cleared first.


        Parameters
        ----------
        start_energy: float
            Kinetic energy of the first data point in eV
        end_energy: float
            Kinetic energy of the end data point in eV
        step: float
            Delta between measurement points in eV
        dwell: float, optional
            Dwell time of the detector in seconds
        pass_energy: float, optional
            Pass energy in eV (default: 5)
        lens: str, optional
            Lens mode (as string)  (default: WideAngleMode)
        scanrange: str, optional
            HSA voltage range for scanning (as string) (default: 40V)
        wich_check:bool, optional
            if True, CheckSpectrumFAT is excecuted after DefineSpectrumFAT (default: True)
        """
        command: str = "DefineSpectrumFAT "
        argument: str = "StartEnergy:{} EndEnergy:{} StepWidth:{} "
        argument += 'DwellTime:{} PassEnergy:{} LensMode:"{}" ScanRange:"{}"'
        argument = argument.format(
            start_energy, end_energy, step, dwell, pass_energy, lens, scanrange
        )
        response = self.sendcommand(command + argument)
        if with_check:
            command = "CheckSpectrumFAT "
            response = self.sendcommand(command + argument)
            self.parse_check_response(response)
        return response

    def defineSFAT(
        self,
        start_energy: float,
        end_energy: float,
        samples: int = 1,
        dwell: float = 0.096,
        lens: str = "WideAngleMode",
        scanrange: str = "40V",
        with_check: bool = True,
    ) -> str:
        """Set measurment parameters of Phoibos (SFAT (Snapshot) mode)

        Send SFAT spectrum (snapshot) specification for subsequent
        acquisition.
        Existing data must be cleared first.

        Note
        -------
        Step width and pass energy are computed automatically
        with reference to the current detector calibration.

        Parameters
        ----------
        start_energy: float
            Kinetic energy of the first data point in eV
        end_energy: float
            Kinetic energy of the end data point in eV
        samples: int, optional
            Number of acquisition samples (default: 1)
        dwell: float, optional
            Dwell time of the detector in seconds (default: 0.096)
        lens: str, optional
            Lens mode (as string)  (default: WideAngleMode)
        scanrange: str, optional
            HSA voltage range for scanning (as string) (default: 40V)
        with_check: bool, optional
            if True, CheckSpectrum is executed after DefinSpectrum  (default: True)
        """
        command: str = "DefineSpectrumSFAT "
        argument: str = "StartEnergy:{} EndEnergy:{} Samples:{} "
        argument += 'DwellTime:{} LensMode:"{}" ScanRange:"{}"'
        argument = argument.format(
            start_energy, end_energy, samples, dwell, lens, scanrange
        )
        response = self.sendcommand(command + argument)
        if with_check:
            command = "CheckSpectrumSFAT"
            response = self.sendcommand(command + argument)
            self.parse_check_response(response)
        return response

    def checkFAT(
        self,
        start_energy: float,
        end_energy: float,
        step: float,
        dwell: float = 0.096,
        pass_energy: float = 5,
        lens: str = "WideAngleMode",
        scanrange: str = "40V",
    ) -> str:
        """Validate FAT spectrum specification.

        Validate FAT spectrum specification without setting
        it for subsequent acquisition. The existing acquisition
        status will be kept.


        Parameters
        ----------
        start_energy: float
            Kinetic energy of the first data point in eV
        end_energy: float
            Kinetic energy of the end data point in eV
        step: float
            Delta between measurement points in eV
        dwell: float, optional
            Dwell time of the detector in seconds  (default: 0.096)
        pass_energy: float, optional
            Pass energy in eV (default: 5)
        lens: str, optional
            Lens mode (as string) (default: WideAngleMode)
        scanRange: str, optional
            HSA voltage range for scanning (as string) (default: 40V)
        """
        command: str = "CheckSpectrumFAT "
        argument: str = "StartEnergy:{} EndEnergy:{} StepWidth:{} "
        argument += 'DwellTime:{} PassEnergy:{} LensMode:"{}" ScanRange:"{}"'
        argument = argument.format(
            start_energy, end_energy, step, dwell, pass_energy, lens, scanrange
        )
        response = self.sendcommand(command + argument)
        self.parse_check_response(response)
        return response

    def checkSFAT(
        self,
        start_energy: float,
        end_energy: float,
        samples: int = 1,
        dwell: float = 0.096,
        lens: str = "WideAngleMode",
        scanrange: str = "40V",
    ) -> str:
        """Validate SFAT spectrum specification.

        Validate SFAT spectrum specification without setting
        it for subsequent acquisition. The existing acquisition
        status will be kept.


        Parameters
        ----------
        start_energy: float
            Kinetic energy of the first data point in eV
        end_energy: float
            Kinetic energy of the end data point in eV
        samples: int, optional
            Number of acquisition samples (default: 1)
        dwell: float, optional
            Dwell time of the detector in seconds (default 0.096)
        pass_energy: float, optional
            Pass energy in eV (default 5)
        lens: str, optional
            Lens mode (as string) (default: WideAngleMode)
        scanRange: str, optional
            HSA voltage range for scanning (as string) (default: 40V)
        """
        command: str = "CheckSpectrumSFAT "
        argument: str = "StartEnergy:{} EndEnergy:{} Samples:{} "
        argument += 'DwellTime:{} LensMode:"{}" ScanRange:"{}"'
        argument = argument.format(
            start_energy, end_energy, samples, dwell, lens, scanrange
        )
        response = self.sendcommand(command + argument)
        self.parse_check_response(response)
        return response

    def parse_check_response(self, response: str) -> None:
        """
        [TODO:summary]

        [TODO:description]

        Parameters
        ----------
        response
            [TODO:description]

        Returns
        -------
        None
            [TODO:description]
        """

        for i in response[10:].split():
            key, item = i.split(":", 2)
            try:
                self.param[key] = int(item)
            except ValueError:
                try:
                    self.param[key] = float(item)
                except ValueError:
                    self.param[key] = item[1:-1]

    def get_analyzer_parameter(self) -> None:
        """Store the analyzer parameter in self.param"""
        parameters = [
            "NumEnergyChannels",
            "NumNonEnergyChannels",
            "Detector Voltage",
            "Bias Voltage Electrons",
            "Screen Voltage",
        ]
        for parameter_name in parameters:
            command = 'GetAnalyzerParameterValue ParameterName:"{}"'.format(
                parameter_name
            )
            key, item = parse_analyzer_parameter(self.sendcommand(command))
            self.param[key] = item

    def validate(self) -> str:
        """Validate parameters

        Returns
        -------
        str
            Response of "ValidateSpectrum" command.
            "key:value" list of the actual parameter values of the spectrum command
        """
        response = self.sendcommand("ValidateSpectrum")
        self.parse_check_response(response)
        self.get_analyzer_parameter()
        self.get_non_energy_channel_info()
        return response

    def set_safe_state(self) -> str:
        """Set the davice into safe state

        Returns
        --------
        str:
            Response of the requested command ("OK")
        """
        response = self.sendcommand("SetSafeState")
        return response

    def start(self, setsafeafter: bool = True) -> str:
        """Start data acquisition.

        Before acquisition, spectum must be validated.
        During measuments, the current status is shown.

        Parameters
        ----------
        setsafeafter: bool, optional
            Specifies whether the analyzer should be set into the safe
            state after the scan or not (Boolean value, as string).
            If set to False the detector voltage is not ramped down
            after the scan and prone to damage by other sources (like ion sources).
            (default: True)

        Returns
        -------
        str
            Response of start command ("OK")
        """
        if setsafeafter:
            command: str = "Start"
        else:
            command = 'Start SetSafeStateAfter:"false"'
        response = self.sendcommand(command)
        if isinstance(self.param["Samples"], int) and isinstance(
            self.param["DwellTime"], float
        ):
            estimate_duration: float = self.param["DwellTime"] * self.param["Samples"]
            sleep(estimate_duration)
        else:
            raise RuntimeError("DwellTime or Samples are wront type")
        status: str = self.get_status()
        while "running" in status:
            sleep(10)
            status = self.get_status()
        return response

    def clear(self) -> str:
        """Clear the internal spectrum buffer and set controllers state to idle.

        Returns
        -------
        str
            Response of "ClearSpectrum" command.
        """
        self.data = []  # for sureness
        return self.sendcommand("ClearSpectrum")

    def get_status(self) -> str:
        """Return information about the status and the progress of the acquisition.

        Response syntax is:
        Ok ControllerState:<ContState> NumberOf AcquiredPoints:<NumPts> [optional: Message:<Text> Details: <Text>]

        ContState:

        * idle
        * validated
        * running
        * paused
        * finished
        * aborted
        * error

        Returns
        -------
        str
            Status
        """
        return self.sendcommand("GetAcquisitionStatus")

    def get_data(self) -> list:
        """Get the intensity map data from the buffer and stored in self.data

        Returns
        -------
        list
            Intensity map data (1D), same data are stored in self.data
        """
        data: str = ""
        status: dict = {}
        for i in self.get_status()[10:].split():
            key, item = i.split(":")
            try:
                status[key] = int(item)
            except ValueError:  # item is string with quotations
                status[key] = item
        assert status["ControllerState"] == "finished"
        request_str: str = "?{:04X} GetAcquisitionData FromIndex:0 ToIndex:{}".format(
            self.id, status["NumberOfAcquiredPoints"] - 1
        )
        self.id += 1
        self.sock.sendtext(request_str)
        data = self.sock.recvtext(byte_size=8192)
        while "]" not in data:
            data += self.sock.recvtext(byte_size=8192)
        self.data = [float(i) for i in data[16:-2].split(",")]
        return self.data

    def get_non_energy_channel_info(self) -> None:
        """Read information about non energy (i.e. Angle) channel

        The data are stored in the self.param property
        """
        response = self.sendcommand('GetSpectrumDataInfo ParameterName:"OrdinateRange"')
        tmp = response[10:-1].split()[1:]
        self.param["Angle_Unit"] = tmp[0].split(":")[-1][1:-1]
        self.param["Angle_min"] = float(tmp[1].split(":")[-1])
        self.param["Angle_max"] = float(tmp[2].split(":")[-1])

    def get_excitation_energy(self) -> None:
        """Read the **recoreded** Photon energy information

        The value is used in the itx file as "Excitation Energy"
        """
        command = 'GetDeviceParameterValue ParameterName:"ex_energy" '
        command += 'DeviceCommand:"UVS.Source"'
        response: str = self.sendcommand(command)
        self.param["ExcitationEnergy"] = float(
            response[10:-1].split()[-1].split()[-1].split(":")[-1]
        )

    def set_excitation_energy(self, excitation_energy: float) -> str:
        """Change the **recoreded** Excitation photon energy value.

        Note:
            Actual photon energy is not affected.

        Parameters
        -----------
        excitation_energy: float
            Photon energy for excitation.
        """
        command = 'SetDeviceParameterValue ParameterName:"ex_energy" '
        command += 'DeviceCommand:"UVS.Source" Value:{}'
        command = command.format(excitation_energy)
        response: str = self.sendcommand(command)
        self.get_excitation_energy()
        return response

    def scan(self, num_scan: int = 1, setsafeafter: bool = True) -> list[float]:
        """Execut the multiple scanning

        Parameters
        -----------
        num_scan: int, optional
            number of scan  (default: 1)
        setsafeafter: bool, optional
            Specifies whether the analyzer should be set into the safe
            state after the scan or not (Boolean value, as string).
            If set to False the detector voltage is not ramped down
            after the scan and prone to damage by other sources (like ion sources).
            (default: True)

        Returns
        ---------
        data: list[float]
            intensity map data.  (The same data are stored as self.data)
        """
        self.param["num_scan"] = num_scan
        data: list = []
        for _ in range(num_scan):
            self.start(setsafeafter=setsafeafter)
            data += self.get_data()
            self.clear()
        if num_scan > 1:
            data = np.array(data).reshape(num_scan, -1).sum(axis=0).tolist()
        self.data = data
        return data

    def save_data(
        self,
        filename: str,
        spectrum_id: int,
        comment: str = "",
        measure_mode: Measure_type = "FAT",
    ) -> None:
        """Save the data as itx format

        Parameters
        ----------
        filename: str
            file name of the data
        spectrum_id: int
            Spectrum_ID
        comment: str, optional
            comment string stored in itx file. (default: "")
        measure_mode: Measure_type, optional
            Measure mode name (FAT or SFAT) (default: FAT)
        """
        itx_data = itx(
            self.data,
            self.param,
            spectrum_id,
            comment=comment,
            measure_mode=measure_mode,
        )
        with open(filename, "w") as itx_file:
            itx_file.write(itx_data)


def parse_analyzer_parameter(response: str) -> tuple[str, int | float]:
    r"""Parse the analyzer parameter, especially for NumNonEnergyChannels:

    Examples
    -----------

    '!0016 OK: Name:"NumNonEnergyChannels" Value:200\n'
        -> ("NumNonEnergyChannels", 200)
    """
    res = response[10:].rsplit(" ", 1)
    try:
        output = (res[0].split(":")[-1][1:-1], int(res[1].split(":")[-1]))
    except ValueError:
        output = (res[0].split(":")[-1][1:-1], float(res[1].split(":")[-1]))
    return output
