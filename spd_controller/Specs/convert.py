#!/usr/bin/env python3

from datetime import UTC, datetime
from typing import Literal

import numpy as np

Measure_type = Literal["FAT", "SFAT"]
WORKFUNCTION_ANALYZER = 4.401

header_template = """IGOR
X //Created Date (UTC): {}
X //Created by: R. Arafune
X //Acquisition Parameters:
X //Scan Mode         = {}
X //User Comment      = {}
X //Analysis Mode     = UPS
X //Lens Mode         = {}
X //Lens Voltage      = {}
X //Spectrum ID       = {}
X //Analyzer Slits    = 1:0.5x20\\B:open
X //Number of Scans   = {}
X //Number of Samples = {}
X //Scan Step         = {}
X //DwellTime         = {}
X //Excitation Energy = {}
X //Kinetic Energy    = {}
X //Pass Energy       = {}
X //Bias Voltage      = {}
X //Detector Voltage  = {}
X //WorkFunction      = {}
"""

DIGIT_ID = 3


def itx(
    data: list[float] | list[list[float]],
    param: dict[str, str | float | int],
    spectrum_id: int,
    num_scan: int = 1,
    comment: str = "",
    measure_mode: Measure_type = "FAT",
    *,
    counts: bool = True,
    correct_angle: bool = True,
) -> str:
    """Build the the itx-style data from the intensity map.

    Parameters
    ----------
    data: list[float]
        Intensity data
    param: dict[ str, str|float|int]
        Spectrum parameter
    spectrum_id: int
        Unique id for spectrum
    num_scan: int
        Number of scan.
    comment: str
        Comment string.  Used in "//User Comment"
    measure_mode : str
        Measurement mode (FAT/SFAT)
    counts: bool
        if True, the unit of the intensity is counts.
    correct_angle : bool
        if True, correct the emission angle
    """
    itx: str = ""
    if "num_scan" in param and num_scan == 1 and isinstance(param["num_scan"], int):
        num_scan = param["num_scan"]
    itx = header(
        param=param,
        spectrum_id=spectrum_id,
        num_scan=num_scan,
        comment=comment,
        measure_mode=measure_mode,
    )
    wavename: str = "ID_" + str(spectrum_id).zfill(DIGIT_ID)
    if measure_mode == "FAT":
        itx += ("WAVES/S/N=({},{}) '" + wavename + "'\nBEGIN\n").format(
            param["NumNonEnergyChannels"],
            param["Samples"],
        )
    else:
        itx += ("WAVES/S/N=({},{}) '" + wavename + "'\nBEGIN\n").format(
            param["NumNonEnergyChannels"],
            param["NumEnergyChannels"],
        )
    if isinstance(param["NumNonEnergyChannels"], int):
        data = np.array(data).reshape(param["NumNonEnergyChannels"], -1).tolist()
    else:
        msg = "NumNonEnergyChannels should be int."
        raise RuntimeError(msg)
    for line in data:
        assert isinstance(line, list)
        itx += " ".join([str(_) for _ in line])
        itx += "\n"
    if (
        isinstance(param["Angle_min"], float)
        and isinstance(param["Angle_max"], float)
        and isinstance(param["NumNonEnergyChannels"], int)
    ):
        if correct_angle:
            angle_max, angle_min = correct_angle_region(
                param["Angle_min"],
                param["Angle_max"],
                param["NumNonEnergyChannels"],
            )
        else:
            angle_max, angle_min = param["Angle_min"], param["Angle_max"]
    else:
        msg = "Angle_min and Angle_max should be float."
        raise RuntimeError(msg)

    itx += "END\n"
    itx += "X SetScale /I x, {}, {}, \"{}\", '{}'\n".format(
        angle_max,
        angle_min,
        param["Angle_Unit"],
        wavename,
    )
    itx += "X SetScale /P y, {}, {},  \"eV\", '{}'\n".format(
        param["StartEnergy"],
        param["StepWidth"],
        wavename,
    )
    if counts:
        itx += f"X SetScale /I d, 0, 0, \"counts (Intensity)\", '{wavename}'\n"
    else:
        itx += f"X SetScale /I d, 0, 0, \"cps (Intensity)\", '{wavename}'\n"
    return itx


def correct_angle_region(
    angle_min: float,
    angle_max: float,
    num_pixel: int,
) -> tuple[float, float]:
    """Correct the angle value to fit igor.

    Parameters
    ----------
    angle_min: float
        Minimum angle of emission
    angle_max: float
        Maximum angle of emission
    num_pixel: int
        The number of pixels for non-energy channels (i.e. angle)

    Returns
    -------
    tuple[float, float]
        minimum angle value and maximum angle value
    """
    diff: float = ((angle_max - angle_min) / num_pixel) / 2
    return angle_min + diff, angle_max - diff


def header(
    param: dict[str, int | float | str],
    spectrum_id: int,
    num_scan: int = 1,
    comment: str = "",
    measure_mode: Measure_type = "FAT",
) -> str:
    """Make itx file header.

    Parameters
    ----------
    param: dict[ str, str | float | int]
        Spectrum parameter
    spectrum_id: int
        Unique id for spectrum
    num_scan: int
        Number of scan.
    comment: str
        Comment string.  Used in "//User Comment"
    measure_mode : Measure_type
        Measurement mode (FAT/SFAT)

    Returns
    -------
    str
        Header part of itx
    """
    mode = "Fixed Analyzer Transmission" if measure_mode == "FAT" else "Snapshot"
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")
    if "User Comment" in param:
        assert isinstance(param["User Comment"], str | None)
        comment += ";" + param["User Comment"]
    return header_template.format(
        now,
        mode,
        comment,
        param["LensMode"],
        param["ScanRange"],
        spectrum_id,
        num_scan,
        param["Samples"],
        param["StepWidth"],
        param["DwellTime"],
        param["ExcitationEnergy"],
        param["StartEnergy"],
        param["PassEnergy"],
        param["Bias Voltage Electrons"],
        param["Detector Voltage"],
        WORKFUNCTION_ANALYZER,
    )
