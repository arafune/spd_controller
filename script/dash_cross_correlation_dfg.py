#!/usr/bin/env python3
"""Dash based application for measuring the temporal overlapping by using DFG"""

import argparse
import numpy as np
from numpy.typing import NDArray

from typing import Literal
from logging import DEBUG, INFO, Formatter, Logger, StreamHandler, getLogger
from enum import Enum

from pathlib import Path
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html

import plotly.express as px

from spd_controller.sigma import sc104
from ThorlabsPM100 import USBTMC, ThorlabsPM100

LOGLEVELS = (DEBUG, INFO)
LOGLEVEL = LOGLEVELS[0]
logger = getLogger(__name__)
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
formatter = Formatter(fmt)
handler = StreamHandler()
handler.setLevel(LOGLEVEL)
logger.setLevel(LOGLEVEL)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


inst = USBTMC()
power_meter = ThorlabsPM100(inst=inst)
power_meter.sense.power.dc.range.auto = "ON"
power_meter.input.pdiode.filter.lpass.state = 0
power_meter.sense.average.count = 100

sc104 = sc104.SC104()


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

external_stylesheets = [dbc.themes.MATERIA]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="CrossCorrelation with DFG",
    update_title=None,
    suppress_callback_exceptions=True,
)


file_name_input = dcc.Input(
    id="filename",
    type="text",
    debounce=True,
    placeholder="File name",
    persistence=True,
    persistence_type="local",
    required=True,
    style={
        "width": "70%",
        "display": "inline-block",
        "verticalAligh": "center",
        "margin-left": "10%",
    },
)

start_position_input = dcc.Input(
    id="initial_position",
    type="number",
    debounce=True,
    min=0,
    max=400,
    step=0.01,
    required=True,
    placeholder="Initial position (mm)",
    persistence=True,
    persistence_type="local",
    style={"width": "20%", "margin-left": "10%"},
)

end_position_input = dcc.Input(
    id="end_position",
    type="number",
    debounce=True,
    min=0,
    max=400,
    step=0.01,
    required=True,
    placeholder="End position (mm)",
    persistence=True,
    persistence_type="local",
    style={"width": "20%", "margin-left": "10%"},
)

step_position_input = dcc.Input(
    id="step_position",
    type="number",
    debounce=True,
    min=0,
    max=1000,
    step=1,
    required=True,
    placeholder="step position (µm)",
    persistence=True,
    persistence_type="local",
    style={"width": "20%", "margin-left": "10%"},
)

measurement_start_button = html.Button(
    "Measurement start",
    id="measurement_start_button",
    disabled=True,
    n_clicks=0,
    style={
        "margin-left": "2%",
        "color": "black",
        "padding": "1px 4px 2px",
        "background": "#FFCCFF",
    },
)

dl_button = dbc.Button(
    "Download data",
    id="dl_button",
    disabled=True,
    n_clicks=0,
    size="sm",
    style={
        "margin-left": "2%",
        "color": "black",
        "padding": "1px 4px 2px",
        "background": "#CCFFFF",
    },
)

buttons = html.Div(
    [measurement_start_button, dl_button, dcc.Download(id="download_data")],
    style={
        "margin": "2em",
        "border-style": "solid",
        "border-radius": "10pt",
        "border-color": "pink",
    },
)

left_col = html.Div(
    [buttons, html.Div(id="current_position"), html.Div(id="current_power")],
    style={"width": "30%", "display": "inline-block"},
)

right_col = html.Div(
    [dcc.Graph(id="cross_correlation_graph", figure=px.line(x=[0.0], y=[0.0]))],
    style={"width": "55%", "display": "inline-block"},
)


app.layout = html.Div(
    [
        html.H1(
            "Cross correlation measurement", id="title", style={"textAlign": "center"}
        ),
        file_name_input,
        start_position_input,
        end_position_input,
        step_position_input,
        left_col,
        right_col,
        dcc.Interval(id="interval", interval=500),
    ],
)


@app.callback(
    Output("download_data", "data"),
    State("filename", "value"),
    Input("dl_button", "n_clicks"),
)
def download_file(dl_filename: str, n_clicks: int):
    """Button to download the data file.

    Parameters
    ----------
    dl_filename: str
        File name of data
    n_clicks: int
        Number of clicks

    Raises
    ------
    Exception:

    """
    if semaphore.is_locked():
        raise Exception("Resource is locked")
    if n_clicks:
        return dcc.send_file(dl_filename)


@app.callback(
    Output("title", "children"),
    State("initial_position", "value"),
    State("end_position", "value"),
    State("step_position", "value"),
    State("filename", "value"),
    Input("measurement_start_button", "n_clicks"),
)
def start_measuring(
    start_position: float,
    end_position: float,
    step_position: float,
    filename: str,
    n_clicks: int,
) -> str:
    if semaphore.is_locked():
        raise Exception("Resource is locked")
    semaphore.lock()

    if n_clicks:
        sc104.move_abs(pos=start_position)
        position = start_position
        with open(filename, "w", buffering=1) as f:
            while position < end_position:
                power_measures = np.array([power_meter.read for _ in range(10)])
                # print(f"{position}\t{power_measures.mean()}\t{power_measures.std()}")
                f.write(
                    f"{position:.4f}\t{power_measures.mean()}\t{power_measures.std()}\n"
                )
                sc104.move_rel(move=step_position, micron=True)
                position = sc104.position()
    semaphore.unlock()
    return "Cross correlation measurement"


@app.callback(
    Output("dl_button", "disabled"),
    Output("measurement_start_button", "disabled"),
    Input("filename", "value"),
)
def activate_button(filename: str) -> tuple[bool, bool]:
    """Activate buttons (Measurement start  & Download data) when the file name is set.

    Parameters
    ----------
    filename: str

    Returns
    -------
    tuple[bool, bool]
    """
    if filename:
        return False, False
    return True, True


@app.callback(
    Output("current_position", "children"),
    Output("current_power", "children"),
    Output("cross_correlation_graph", "figure"),
    State("filename", "value"),
    Input("interval", "n_intervals"),
)
def update_graph(filename: str, n_intervals: int):
    """Updating graph

    Updating the graph of the DFG intensity as a function of the delay line position.

    Parameters
    ----------
    filename: str
        Filename of the data
    n_intervals: int
        Interval time in ms

    Returns
    -------
    tuple
        current position, current power and plotly graph object

    """
    if filename:
        p = Path(filename)
        if not p.exists():
            p.touch()
        if p.stat().st_size > 0:
            data: NDArray[np.float_] = np.loadtxt(filename).T
            try:
                positions = data[0]
                powers = data[1]
                current_position = positions[-1]
                current_power = powers[-1]
            except IndexError:
                pass
            return (
                f"Position: {current_position:.4f}",
                f"Power: {current_power}",
                px.line(x=positions, y=powers).update_layout(
                    xaxis_title="Position", yaxis_title="Power"
                ),
            )
        else:
            return ("Posiiton: Nan", "Power: Nan", px.line(x=[0.0], y=[0.0]))
    return ("Position: Nan", "Power Nan", px.line(x=[0.0], y=[0.0]))


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
