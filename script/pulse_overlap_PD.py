#!/usr/bin/env python3

"""Measure the pulse overlap by using oscilloscope."""

import argparse

import numpy as np
from numpy.typing import NDArray

from spd_controller.sigma import sc104
from spd_controller.texio import gds3502

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--start",
        type=float,
        required=True,
        help="Start position in mm unit.",
    )
    parser.add_argument(
        "--step",
        type=float,
        required=True,
        help="Step in um unit.",
    )
    parser.add_argument(
        "--end",
        type=float,
        required=True,
        help="End position in mm unit",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output file name",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        default=False,
        help="""if set, the mirror moves to "mechanically zero" and then move to the "start position" """,
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=1,
        required=True,
        help="Channel number 1 or 2.",
    )
    args = parser.parse_args()
    assert args.channel in (1, 2)
    s = sc104.SC104()
    if args.reset:
        s.move_to_origin()
    s.move_abs(args.start)
    pos = s.position()
    o = gds3502.GDS3502()
    o.acquire_memory(args.channel)
    header = ["timescale"]
    data: list[NDArray[np.float_]] = [o.timescale]
    while pos < args.end:
        header.append(f"{pos:.4f}")
        data.append(o.acquire_memory(1))
        s.move_rel(args.step, micron=True)
        pos = s.position()
    np.savetxt(args.output, np.array(data).T, delimiter="\t", header="\t".join(header))
