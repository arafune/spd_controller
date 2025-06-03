#!/usr/bin/env python3

import argparse
import yaml
import numpy as np

from time import sleep
from spd_controller.sigma.omec4bf import OMEC4BF
from ThorlabsPM100 import USBTMC, ThorlabsPM100
from numpy.typing import NDArray


def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=str,
        help="""output file name
        if not specified, use the value defined in the input_yaml""",
    )
    parser.add_argument("input_yaml")
    #
    args = parser.parse_args()
    config = load_config(args.input_yaml)
    if args.output:
        config["output_file"] = args.output
    data: list[list[float]] = []
    inst = USBTMC()
    power_meter = ThorlabsPM100(inst=inst)
    #
    threshold = float(config["threshold"])
    #
    if config["power_range"] == "auto":
        power_meter.sense.power.dc.range.auto = "ON"
    else:
        power_meter.sense.power.dc.range.upper = config["power_range"]
    power_meter.sense.correction.wavelength = config["wavelength"]
    # power_meter.sense.power.dc.range.auto = "ON"
    power_meter.input.pdiode.filter.lpass.state = 0
    power_meter.sense.average.count = 100
    #
    omec = OMEC4BF(port=config["setting"]["omec_port"])
    for z in range(config["start_z"], config["end_z"], config["step_z"]):
        omec.move_abs(group=1, axis="x", position=z)
        data_at_z: list[float] = []
        for height in range(
            config["start_height"], config["end_height"], config["step_height"]
        ):
            omec.move_abs(group=1, axis="y", position=height)
            power_measures: NDArray[np.float64] = np.array(
                [power_meter.read for _ in range(10)]
            )
            intensity = power_measures.mean()
            if "verbose" in config["setting"] and config["setting"]["verbose"]:
                print(f"z: {z}, height: {height}, {intensity}")
            if intensity < threshold:
                break
            data_at_z.append(intensity)
        data.append(data_at_z)

    header = f"# start_z:{config['start_z']}, end_z:{config['end_z']}, step_z:{config['step_z']}, "
    header += f"start_height:{config['start_height']}, end_height:{config['end_height']}, step_height:{config['step_height']}"
    header += f", threshold:{config['threshold']}"
    with open(config["output_file"], "w") as f:
        f.write(header + "\n")
        for row in data:
            line = "\t".join(f"{x:.8e}" for x in row)
            f.write(line + "\n")
