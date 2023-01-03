#!/usr/bin/env python3
"""draw polarization dependence"""

import argparse

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", help="file name for data to draw")
    args = parser.parse_args()
    #
    data = np.loadtxt(args.file_name)
    #
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.plot(np.deg2rad(data.T[0]), data.T[1])
    ax.set_rticks([])
    ax.set_rlim([0, None])
    ax.set_title(args.file_name)
    fig.savefig(args.file_name + ".png", dpi=600)
