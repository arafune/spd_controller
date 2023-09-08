#!/usr/bin/env python3
"""Rotate polarizer"""

import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State
from spd_controller.thorlabs.k10cr1 import K10CR1


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
    title="Polarizer rotatation",
    update_title=None,
    suppress_callback_exceptions=True,
)

input_rotation_angle = dbc.Input(
    id="angle_value",
    type="number",
    debounce=True,
    size="lg",
    placeholder="Angle",
    style={
        "width": "20em",
        "display": "inline-block",
        "marginLeft": "3em",
    },
)

relative_rotation_button = dbc.Button(
    "Rotate (relatively)",
    color="primary",
    id="rel_rotate_button",
    style={"display": "inline-block", "marginLeft": "3em"},
)

absolute_rotation_button = dbc.Button(
    "Rotate to this angle",
    color="danger",
    id="abs_rotate_button",
    style={"display": "inline-block", "marginLeft": "3em"},
)


app.layout = html.Div(
    [
        html.H1("Polarizer Rotation", style={"textAlign": "center"}),
        html.Div(
            [input_rotation_angle, relative_rotation_button, absolute_rotation_button],
            style={"display": "flex", "justify-content": "center"},
        ),
    ],
)


@app.callback(
    Output("rel_rotate_button", "style"),
    State("angle_value", "value"),
    Input("rel_rotate_button", "n_clicks"),
)
def rel_rotate_start(angle: float, n_clicks: int) -> dict[str, str]:
    if n_clicks is not None:
        polarizer.move_rel(angle)
        return {"display": "inline-block", "marginLeft": "3em"}


@app.callback(
    Output("abs_rotate_button", "style"),
    State("angle_value", "value"),
    Input("rel_rotate_button", "n_clicks"),
)
def abs_rotate_start(angle: float, n_clicks: int) -> dict[str, str]:
    if n_clicks is not None:
        polarizer.move_abs(angle)
        return {"display": "inline-block", "marginLeft": "3em"}


if __name__ == "__main__":
    polarizer = K10CR1("55274554")
    if not polarizer.ready:
        from unittest.mock import MagicMock

        polarizer = MagicMock()
        polarizer.move_rel = MagicMock(side_effect="moverel")
        polarizer.move_abs = MagicMock(side_effect="moveabs")
    app.run_server(debug=True, host="0.0.0.0", PORT="8051")
