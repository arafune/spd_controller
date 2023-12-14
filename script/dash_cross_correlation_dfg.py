#!/usr/bin/env python3
"""Dash based application for measuring the temporal overlapping by using DFG"""

import argparse

from typing import Literal
from logging import DEBUG, INFO, Formatter, Logger, StreamHandler, getLogger
from enum import Enum

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, dcc, html

# from spd_controller.sigma import sc104
# from ThorlabsPM100 import USBTMC, ThorlabsPM100


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
    title="Polarization analysis",
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
    placeholder="Initial position (mm)",
    persistence=True,
    persistence_type="local",
    style={"width": "20%", "margin-left": "10%"},
)

end_position_input = dcc.Input(
    id="end_position",
    type="number",
    debounce=True,
    placeholder="End position (mm)",
    persistence=True,
    persistence_type="local",
    style={"width": "20%", "margin-left": "10%"},
)

step_position_input = dcc.Input(
    id="step_position",
    type="number",
    debounce=True,
    placeholder="step position (mm)",
    persistence=True,
    persistence_type="local",
    style={"width": "20%", "margin-left": "10%"},
)

measurment_start_button = html.Button(
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
        "display": "inline-block",
        "margin-left": "2%",
        "color": "black",
        "padding": "1px 4px 2px",
        "background": "#CCFFFF",
    },
)

buttons = html.Div(
    [measurment_start_button, dl_button, dcc.Download(id="download_data")],
    style={
        "margin": "2em",
        "border-style": "solid",
        "border-radius": "10pt",
        "border-color": "pink",
    },
)

left_col = html.Div(
    [
        buttons,
    ],
    style={"width": "40%", "display": "inline-block"},
)
right_col = html.Div(
    [],
    style={"width": "40%", "display": "inline-block"},
)


app.layout = html.Div(
    [
        html.H1("Temporal overlap", style={"textAlign": "center"}),
        file_name_input,
        start_position_input,
        end_position_input,
        step_position_input,
        left_col,
        right_col,
        dcc.Interval(id="interval", interval=500),
    ],
)


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
