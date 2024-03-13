#!/usr/bin/env python3

"""Measure the pulse overlap by using oscilloscope."""

import argparse
import time
import numpy as np
from numpy.typing import NDArray
from pathlib import Path
from spd_controller.sigma import sc104
from spd_controller.texio import gds3502
from spd_controller.thorlabs import mff101


class DummyFlipper:
    def __init__(self) -> None:
        self.ready = False

    def flip(self) -> None:
        return None


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
        "--with_fig",
        action="store_true",
        default=False,
        help="""if set, the corresponding display image file is saved.""",
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=1,
        required=True,
        help="The number of the oscilloscope channel (1 or 2).",
    )
    parser.add_argument(
        "--ET",
        action="store_true",
        default=False,
        help="If set, interpolation ET mode.",
    )
    parser.add_argument(
        "--average",
        type=int,
        default=0,
        help="Set average times in acquition. if 0, Sample mode is set.",
    )
    parser.add_argument(
        "--socket",
        action="store_true",
        default=False,
        help="if set, connect Oscilloscopy by socket (Ethernet).",
    )
    parser.add_argument(
        "--flip", action="store_true", default=False, help="if True, use flipper"
    )
    parser.add_argument(
        "--flipper_port",
        type=int,
        required=False,
        default=0,
        help="COM port number, which must be set for Windows.",
    )
    parser.add_argument(
        "--use_trigger_freq",
        action="store_true",
        default=False,
        help="if set, use trigger frequency instead of the measured freqency."
    )
    args = parser.parse_args()
    assert args.channel in (1, 2)
    assert args.average in (0, 2, 4, 8, 16, 32, 64, 128, 256)
    if args.flip:
        if args.flipper_port:
            flipper = mff101.MFF101(args.flipper_port)
            assert flipper.ready, "Check the port number of the flipper."
        else:
            flipper = mff101.MFF101(37003548)
            assert (
                flipper.ready
            ), "If your os is Windows, --flipper_port N (N is the number of COM port) is requred."
        flipper.move_backward()
    else:
        flipper = DummyFlipper()  # type: ignore
    s = sc104.SC104()
    if args.reset:
        s.move_to_origin()
    s.move_abs(args.start, wait=True)
    pos = s.position()
    if args.socket:
        o = gds3502.GDS3502(connection="socket")
    else:
        o = gds3502.GDS3502(connection="usb")
    if args.ET:
        o.set_interpolation_et()
    else:
        o.set_realtime_sampling()
    if args.average == 0:
        o.set_sample_mode()
        waiting_time = 1.0
    else:
        waiting_time = o.set_average_mode(n_average=args.average)
    time.sleep(waiting_time)
    o.acquire_memory(args.channel)
    header = ["timescale"]
    data: list[NDArray[np.float_]] = [o.timescale]
    data_with_flip: list[NDArray[np.float_]] = [o.timescale]
    while pos < args.end:
        if args.use_trigger_freq:
            frequency = o.triger_frequency
        else:
            frequency = o.measure_frequency(args.channel)
        header.append(f"position_{np.round(pos, 3):.3f}@{frequency}")
        data.append(o.acquire_memory(args.channel))
        s.move_rel(args.step, micron=True, wait=True)
        time.sleep(waiting_time)
        if args.flip:
            flipper.flip()
            time.sleep(waiting_time)
            data_with_flip.append(o.acquire_memory(args.channel))
            flipper.flip()
            time.sleep(waiting_time)
        pos = s.position()
        if args.with_fig:
            o.save_image(f'"Disk:/{args.output}_pos_{np.round(pos, 3):.3f}.png"')
    np.savetxt(
        args.output,
        np.array(data).T,
        delimiter="\t",
        header="\t".join(header),
    )
    if args.flip:
        output_name, output_suffix = Path(args.output).stem, Path(args.output).suffix
        np.savetxt(
            output_name + "_with_flip" + output_suffix,
            np.array(data_with_flip).T,
            delimiter="\t",
            header="\t".join(header),
        )
