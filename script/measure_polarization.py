#! /usr/bin/env python3
"""Measure the polarization direction.

The cycle of measuring the laser power and then rotating the polalizer.
"""
import argparse
from pathlib import Path
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from K10CR1.k10cr1 import K10CR1
from numpy.typing import NDArray
from ThorlabsPM100 import USBTMC, ThorlabsPM100

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--step",
        metavar="step_angle_degree",
        type=float,
        nargs=1,
        help="step angle",
        default=1,
    )
    parser.add_argument("--no_graph", type=bool, default=False)
    parser.add_argument("file_name", help="filename for data")
    args = parser.parse_args()
    #
    polarizer = K10CR1("55274554")
    inst = USBTMC()
    power_meter = ThorlabsPM100(inst=inst)
    #
    power_meter.sense.power.dc.range.auto = "ON"
    power_meter.input.pdiode.filter.lpass.state = 0
    power_meter.sense.average.count = 100
    #
    polarizer.home()
    if args.file_name:
        f = open(args.file_name, mode="w")
    for angle in range(0, 360, args.step):
        polarizer.move_rel(args.step)
        polarizer.rd(20)
        sleep(0.01)  # 0.01 s is sufficient waiting time.
        # BUT: by inserting rd(20), sleep can be removed.
        power_measures: NDArray[float] = np.array([power_meter.read for _ in range(10)])
        result = "angle: {}, power: {} ±: {}".format(
            angle,
            power_measures.mean(),
            power_measures.std(),
        )
        print(result)
        if args.file_name:
            f.write(
                f"{angle}\t{power_measures.mean()}\t{power_measures.std()}\n",
            )
    if args.file_name:
        f.close()
    if not args.no_graph:
        data_file = Path(args.file_name)
        data = np.loadtxt(data_file)
        fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
        ax.plot(np.deg2rad(data.T[0]), data.T[1] / np.max(data.T[1]))
        ax.set_rticks([])
        ax.set_rlim([0, None])
        ax.set_title(data_file.stem)
        fig.savefig(data_file.stem + ".png", dpi=600)
