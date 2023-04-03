#!/usr/bin/env python3

from datetime import datetime, timezone

import numpy as np

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
X //WorkFunction      = 4.401
"""


def itx(
    data: list,
    param: dict,
    id: int,
    num_scan: int = 1,
    comment: str = "",
    measure_mode="FAT",
):
    itx: str = ""
    if "num_scan" in param.keys() and num_scan == 1:
        num_scan = param["num_scan"]
    itx = header(
        param=param,
        id=id,
        num_scan=num_scan,
        comment=comment,
        measure_mode=measure_mode,
    )
    if measure_mode == "FAT":
        itx += "WAVES/S/N=({}, {}) 'ID_{:04}'\nBEGIN\n".format(
            param["NumNonEnergyChannels"], param["Samples"], id
        )
    else:
        itx += "WAVES/S/N=({}, {}) 'ID_{:04}'\nBEGIN\n".format(
            param["NumNonEnergyChannels"], param["NumEnergyChannels"], id
        )
    data = np.array(data).reshape(param["NumNonEnergyChannels"], -1).tolist()
    for line in data:
        itx += " ".join([str(_) for _ in line])
        itx += "\n"
    angle_max, angle_min = correct_angle_region(
        param["Angle_min"], param["Angle_max"], param["NumNonEnergyChannels"]
    )
    itx += "END\n"
    itx += "X SetScale /I x, {}, {}, \"{}\", 'ID_{:04}'\n".format(
        angle_max, angle_min, param["Angle_Unit"], id
    )
    itx += "X SetScale /P y, {}, {},  \"eV\", 'ID_{:04}'\n".format(
        param["StartEnergy"], param["StepWidth"], id
    )
    itx += "X SetScale /I d, 0, 0, \"cps (Intensity)\", 'ID_{0:04}'\n".format(id)
    return itx


def correct_angle_region(
    angle_min: float, angle_max: float, num_pixel: int
) -> tuple[float, float]:
    diff: float = ((angle_max - angle_min) / num_pixel) / 2
    return angle_min + diff, angle_max - diff


def header(
    param: dict, id: int, num_scan: int = 1, comment: str = "", measure_mode="FAT"
) -> str:
    if measure_mode == "FAT":
        mode = "Fixed Analyzer Transmission"
    else:
        mode = "Snapshot"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    return header_template.format(
        now,
        mode,
        comment,
        param["LensMode"],
        param["ScaanRange"],
        id,
        num_scan,
        param["Samples"],
        param["StepWidth"],
        param["DwellTime"],
        param["ExcitationEnergy"],
        param["StartEnergy"],
        param["PassEnergy"],
        param["Bias Voltage Electrons"],
        param["Detector Voltage"],
    )
