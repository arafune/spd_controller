#!/usr/bin/env python3
"""Polarization analysis system"""

from __future__ import annotations

from pathlib import Path
from time import sleep
from typing import Literal
from unittest.mock import MagicMock

import dash
import dash_daq as daq
import numpy as np
import plotly.express as px
from dash import Input, Output, State, dcc, html
from numpy.typing import NDArray

try:
    from ThorlabsPM100 import USBTMC, ThorlabsPM100

    from spd_controller.thorlabs.k10cr1 import K10CR1

    polarizer = K10CR1("55274554")
    inst = USBTMC()
    power_meter = ThorlabsPM100(inst=inst)
    power_meter.sense.power.dc.range.auto = "ON"
    power_meter.input.pdiode.filter.lpass.state = 0
    power_meter.sense.average.count = 100
except (ModuleNotFoundError, ImportError):
    from random import random
    from unittest.mock import MagicMock, PropertyMock

    def side(dummy_angle_deg: int):
        sleep(1.5)
        return None

    polarizer = MagicMock()
    polarizer.move_rel = MagicMock(side_effect=side)
    power_meter = MagicMock()
    type(power_meter).read = PropertyMock(
        side_effect=[random() / 100 for _ in range(3600)]
    )


class Semaphore:
    def __init__(self, filename: str = "semaphore_pol.txt") -> None:
        self.filename = filename
        with open(self.filename, "w") as f:
            f.write("done")

    def lock(self) -> None:
        with open(self.filename, "w") as f:
            f.write("working")

    def unlock(self) -> None:
        with open(self.filename, "w") as f:
            f.write("done")

    def is_locked(self) -> bool:
        return open(self.filename, "r").read() == "working"


semaphore = Semaphore()

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Polarization analysis",
    update_title=None,
    suppress_callback_exceptions=True,
)

filename_input_style: dict[str, str] = {
    "width": "70%",
    "display": "inline-block",
    "verticalAlign": "center",
    "margin-left": "10%",
}

file_name_input = dcc.Input(
    id="filename",
    type="text",
    debounce=True,
    placeholder="File name",
    persistence=True,
    persistence_type="local",
    style=filename_input_style,
)


angle_step_input = html.Div(
    [
        html.P(
            "Angle step (deg): ",
            style={"display": "inline-block", "margin-left": "11%"},
        ),
        daq.NumericInput(
            id="angle_step_input",
            value=1,
            min=1,
            max=359,
            style={"display": "inline-block", "margin-left": "2%"},
        ),
    ]
)


measurment_start_button = html.Button(
    "Measurement start",
    id="measurement_start_button",
    disabled=True,
    n_clicks=0,
    style={
        "margin-left": "10%",
        "color": "black",
        "padding": "1px 4px 2px",
        "background": "#FFCCFF",
    },
)

dl_button = html.Button(
    "Download data",
    id="dl_button",
    disabled=True,
    n_clicks=0,
    style={
        "display": "inline-block",
        "margin-left": "15%",
        "color": "black",
        "padding": "1px 4px 2px",
        "background": "#CCFFFF",
    },
)

buttons = html.Div(
    [measurment_start_button, dl_button, dcc.Download(id="download_data")]
)

save_sw_style = {
    "display": "inline-block",
    "verticalAlign": "center",
    "margin-left": 15,
}

current_angle = daq.LEDDisplay(
    id="current_angle_display",
    label="Angle (deg)",
    value="0.00",
    size=80,
    color="red",
    style={},
)  # dash.development.base_component.ComponentMeta'>

current_power = daq.LEDDisplay(
    id="current_power_display",
    label="Power (mW)",
    value="0.00",
    size=80,
    color="red",
    style={},
)

left_col = html.Div(
    [file_name_input, angle_step_input, buttons, current_angle, current_power],
    style={"width": "40%", "display": "inline-block"},
)
right_col = html.Div(
    [
        dcc.Graph(
            id="polarization_graph",
            figure=px.line_polar(
                r=[2, 3, 4, 5],
                theta=[0, 10, 30, 90],
                start_angle=0,
                direction="counterclockwise",
            ),
        )
    ],
    style={"display": "inline-block", "width": "50%"},
)
app.layout = html.Div(
    [
        html.H1("Polarization Analysis", style={"textAlign": "center"}),
        dcc.Interval(id="interval", interval=500),
        html.Div([left_col, right_col]),
        html.Div(id="status"),
    ],
)


@app.callback(
    Output("download_data", "data"),
    State("filename", "value"),
    Input("dl_button", "n_clicks"),
)
def download_file(dl_filename: str, n_clicks: int):
    if semaphore.is_locked():
        raise Exception("Resource is locked")
    if n_clicks > 0:
        return dcc.send_file(dl_filename)


@app.callback(
    Output("status", "children"),
    State("angle_step_input", "value"),
    State("filename", "value"),
    Input("measurement_start_button", "n_clicks"),
)
def start_measurement(angle_increment: int, filename: str, n_clicks: int) -> str:
    if semaphore.is_locked():
        raise Exception("Resource is locked")
    semaphore.lock()
    #
    if n_clicks > 0:
        polarizer.home()
        #
        if filename:
            with open(filename, "w", buffering=1) as f:
                for angle in range(0, 360, angle_increment):
                    polarizer.moverel(angle_increment)
                    polarizer.rd(20)
                    sleep(0.01)
                    power_measures = np.array([power_meter.read for _ in range(10)])
                    print(
                        "{}\t{}±{}".format(
                            angle, power_measures.mean(), power_measures.std()
                        )
                    )
                    f.write(
                        "{}\t{}\t{}\n".format(
                            angle, power_measures.mean(), power_measures.std()
                        )
                    )
        else:
            semaphore.unlock()
            return "Status: No file name"
    semaphore.unlock()
    return "Status: Done"


@app.callback(
    Output("dl_button", "disabled"),
    Output("measurement_start_button", "disabled"),
    Input("filename", "value"),
)
def enable_meas_start_sw(filename: str) -> tuple[bool, bool]:
    if filename:
        return False, False
    else:
        return True, True


@app.callback(
    Output("current_angle_display", "value"),
    Output("current_power_display", "value"),
    Output("polarization_graph", "figure"),
    State("filename", "value"),
    Input("interval", "n_intervals"),
)
def update_graph(filename: str, n_intervals: int):
    if filename:
        p = Path(filename)
        if not p.exists():
            p.touch()
        if p.stat().st_size > 0:
            data: NDArray[np.float_] = np.loadtxt(filename).T
            try:
                angles = data[0]
                powers = data[1]
                current_angle = angles[-1]
                current_power = powers[-1]
            except IndexError:
                angles: NDArray[np.float_] = np.array([0])
                powers: NDArray[np.float_] = np.array([0])
                current_angle = 0
                current_power = 0
            return (
                "{:.0f}".format(current_angle),
                "{:.2f}".format(current_power * 1000),
                px.line_polar(
                    r=powers * 1000,
                    theta=angles,
                    start_angle=0,
                    direction="counterclockwise",
                ),
            )
        else:
            return (
                0.0,
                0.0,
                px.line_polar(
                    r=[0],
                    theta=[0],
                    start_angle=0,
                    direction="counterclockwise",
                ),
            )
    return (
        0.0,
        0.0,
        px.line_polar(
            r=[0],
            theta=[0],
            start_angle=0,
            direction="counterclockwise",
        ),
    )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
