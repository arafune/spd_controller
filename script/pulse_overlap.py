#!/usr/bin/env pyuthon3

"""Measure the pulse overlap by using oscilloscope"""

import argparse
import numpy as np
import spd_controller.texio.gds3502 as gds3502
import spd_controller.sigma.sc104 as sc104

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--start", type=float, required=True, help="Start position in mm unit."
    )
    parser.add_argument("--step", type=float, required=True, help="Step in um unit.")
    parser.add_argument(
        "--end", type=float, required=True, help="End position in mm unit"
    )
    parser.add_argument("--output", type=float, required=True, help="Output file name")
    args = parser.parse_args()
    s = sc104.SC104()
    s.move_to_origin()
    s.move_abs(args.start)
    pos = s.position()
    o = gds3502.GDS3502()
    data = []
    while pos < args.end:
        data.append(o.acquire_memory(1))
        s.move_rel(args.step, micron=True)
        pos = s.position()
    np.savetxt(args.output, np.array(data))
