#!/usr/bin/env pyuthon3

"""Measure the pulse overlap by using oscilloscope."""

import argparse

import numpy as np
from numpy.typing import NDArray

from spd_controller.sigma import sc104
from spd_controller.texio import gds3502

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--start", type=float, required=True, help="Start position in mm unit.",
    )
    parser.add_argument("--step", type=float, required=True, help="Step in um unit.")
    parser.add_argument(
        "--end", type=float, required=True, help="End position in mm unit",
    )
    parser.add_argument("--output", type=float, required=True, help="Output file name")
    args = parser.parse_args()
    s = sc104.SC104(port="COM3")
    s.move_to_origin()
    s.move_abs(args.start)
    pos = s.position()
    o = gds3502.GDS3502()
    o.acquire_memory(2)
    header = ["timescale"]
    data: list[NDArray] = [o.timescale]
    while pos < args.end:
        header.append(f"{pos:.4f}")
        data.append(o.acquire_memory(2))
        s.move_rel(args.step, micron=True)
        pos = s.position()
    np.savetxt(args.output, np.array(data).T, delimiter="\t", header="\t".join(header))
