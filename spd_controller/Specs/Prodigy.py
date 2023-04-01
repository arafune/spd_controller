#!/usr/bin/env python
"""Class for Prodigy remote_in"""

import socket
from time import sleep

import numpy as np

import spd_controller.Specs.convert as convert

from .. import SocketClient

BUFSIZE = 1024


class RemoteIn(SocketClient):
    """Class for Prodigy Remote In"""

    def __init__(self, host: str = "144.213.126.140", port: int = 7010) -> None:
        super().__init__(host=host, port=port)
        self.id: int = 1
        self.samples: int = 0
        self.param: dict[str, int | float | str] = {}
        self.data: list[float] = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def sendcommand(self, text: str, buffsize: int = BUFSIZE) -> str:
        """Send command"""
        request_str: str = "?" + format(self.id, "04X") + " " + text
        self.id += 1
        self.sendtext(request_str)
        return self.recvtext(buffsize)

    def connect(self) -> str:
        """Open connection to SpecsLab Prodigy

        Returns
        --------
        str: Responce of "Connect command"
            Ex. '!0001 OK: ServerName:"SpecsLab Prodigy 4.86.2-r103043 " ProtocolVersion:1.18\n'
        """
        return self.sendcommand("Connect")

    def disconnect(self) -> str:
        """Close connection to SpecsLab Prodigy

        Returns -------- str: Responce of "Disconnect command"
            Ex. '!0005 OK\n'
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
        dwell: float
            Dwell time of the detector in seconds
        pass_energy: float
            Pass energy in eV
        lens: str
            Lens mode (as string)
        scanrange: str
            HSA voltage range for scanning (as string)
        wich_check:bool
            if True, CheckSpectrumFAT is excecuted after DefineSpectrumFAT
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
        Samples: int
            Number of acquisition samples (Default: 1)
        dwell: float
            Dwell time of the detector in seconds
        pass_energy: float
            Pass energy in eV
        lens: str
            Lens mode (as string)
        scanrange: str
            HSA voltage range for scanning (as string)
        with_check: bool
            if True, CheckSpectrum is executed after DefinSpectrum
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
        dwell: float
            Dwell time of the detector in seconds
        pass_energy: float
            Pass energy in eV
        lens: str
            Lens mode (as string)
        ScanRange: HSA voltage range for scanning (as string)
        """
        command: str = "CheckSpectrumFAT "
        argument: str = "CheckSpectrumFAT StartEnergy:{} EndEnergy:{} StepWidth:{} "
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
        Samples: int
            Number of acquisition samples (Default: 1)
        dwell: float
            Dwell time of the detector in seconds
        pass_energy: float
            Pass energy in eV
        lens: str
            Lens mode (as string)
        ScanRange: HSA voltage range for scanning (as string)
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
        for i in response[10:].split():
            key, item = i.split(":", 1)
            try:
                self.param[key] = int(item)
            except ValueError:
                try:
                    self.param[key] = float(item)
                except ValueError:
                    self.param[key] = item[1:-1]

    def get_analyzer_parameter(self) -> None:
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
        response = self.sendcommand("ValidateSpectrum")
        self.get_analyzer_parameter()
        self.get_non_energy_channel_info()
        return response

    def start(self, setsafeafter: bool = True) -> str:
        if setsafeafter:
            command: str = "Start"
        else:
            command = 'Start SetSafeStartAfter:"false"'
        response = self.sendcommand(command)
        estimate_duration: float = self.param["DwellTime"] * self.param["Samples"]
        sleep(estimate_duration)
        status: str = self.get_status()
        while "running" in status:
            sleep(10)
            status = self.get_status()
        return response

    def clear(self) -> str:
        self.data = []  # for sureness
        return self.sendcommand("ClearSpectrum")

    def get_status(self) -> str:
        return self.sendcommand("GetAcquisitionStatus")

    def get_data(self) -> list:
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
        self.sendtext(request_str)
        data = self.recvtext(byte_size=8192)
        while "]" not in data:
            data += self.recvtext(byte_size=8192)
        self.data = [float(i) for i in data[16:-2].split(",")]
        return self.data

    def get_non_energy_channel_info(self):
        response = self.sendcommand('GetSpectrumDataInfo ParameterName:"OrdinateRange"')
        tmp = response[10:-1].split()[1:]
        self.param["Angle_Unit"] = tmp[0].split(":")[-1][1:-1]
        self.param["Angle_min"] = float(tmp[1].split(":")[-1])
        self.param["Angle_max"] = float(tmp[2].split(":")[-1])

    def get_excitation_energy(self) -> None:
        command = 'GetDeviceParameterValue ParameterName:"ex_energy" '
        command += 'DeviceCommand:"UVS.Source"'
        response: str = self.sendcommand(command)
        self.param["ExcitationEnergy"] = float(
            response[10:-1].split()[-1].split()[-1].split(":")[-1]
        )

    def set_excitation_energy(self, excitation_energy: float) -> str:
        command = 'SetDeviceParameterValue ParameterName:"ex_energy" '
        command += 'DeviceCommand:"UVS.Source" Value:{}'
        command = command.format(excitation_energy)
        response: str = self.sendcommand(command)
        self.get_excitation_energy()
        return response

    def scan(self, num_scan: int = 1) -> list[float]:
        self.param["num_scan"] = num_scan
        data: list = []
        for _ in range(num_scan):
            self.start(setsafeafter=True)
            data += self.get_data()
            self.clear()
        if num_scan > 1:
            data = np.array(data).reshape(num_scan, -1).sum(axis=0).tolist()
        self.data = data
        return data

    def save_data(
        self, filename: str, id: int, comment: str = "", measure_mode: str = "FAT"
    ) -> None:
        itx = convert.itx(
            self.data, self.param, id, comment=comment, measure_mode=measure_mode
        )
        with open(filename, "w") as itx_file:
            itx_file.write(itx)


def parse_analyzer_parameter(response: str) -> tuple[str, int | float]:
    """
    '!0016 OK: Name:"NumNonEnergyChannels" Value:200\n'
        -> ("NumNonEnergyChannels", 200)
    """
    res = response[10:].rsplit(" ", 1)
    try:
        output = (res[0].split(":")[-1][1:-1], int(res[1].split(":")[-1]))
    except ValueError:
        output = (res[0].split(":")[-1][1:-1], float(res[1].split(":")[-1]))
    return output
