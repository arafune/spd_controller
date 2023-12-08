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

app.layout = html.Div(
    [
        html.H1("Temporal overlap", style={"textAlign": "center"}),
        dcc.Interval(id="interval", interval=500),
    ],
)


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
