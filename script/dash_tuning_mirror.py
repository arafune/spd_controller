#!/usr/bin/env python3
"""Dash based application for tuning mirror and flipper."""


import dash
import dash_bootstrap_components as dbc
from _dash_tuning_mirror_layout import (
    flipper1_button,
    flipper2_button,
    mirror_component,
)
from dash import dcc, html

from spd_controller.newport import picomotor8742
from spd_controller.newport.picomotor8742 import Axis
from spd_controller.thorlabs import mff101

external_stylesheets = [dbc.themes.MATERIA]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="mirror tuning",
    update_title="",
    suppress_callback_exceptions=True,
)


app.layout = html.Article(
    children=[
        html.H1("Turning Mirrors/flippers", style={"text-align": "center"}),
        dcc.Interval(id="realtime_interval", interval=1000),
        html.Div([]),  # flipper
        flipper1_button,
        flipper2_button,
        html.Div(
            [
                mirror_component(nl_order=3),
                mirror_component(nl_order=1),
            ],
        ),
    ],
)


def move_mirror_indefinitely(axis: Axis, action: str) -> bool:
    """Move mirror indefinitely.

    Parameters
    ----------
    axis: int
        Axis number
    action: str
        "cw", "ccw", or other (= "stop")

    Returns
    -------
    bool
        Return true/false to set "disable" property of the dash component
    """
    if action == "ccw":
        picomotor.move_indefinitely(axis, positive=False)
        return True
    if action == "cw":
        picomotor.move_indefinitely(axis, positive=True)
        return True
    picomotor.force_stop(axis)
    return False


if __name__ == "__main__":
    flipper1 = mff101.MFF101("37003548")
    if not flipper1.ready:
        pass  # goto "mockmode"
    flipper2 = mff101.MFF101("37003278")
    if not flipper2.ready:
        pass  # goto "mockmode"
    picomotor = picomotor8742.Picomotor8742(host="144.213.126.101")
    try:
        picomotor.connect()
    except TimeoutError:
        pass  # goto "mockmode"
    app.run_server(debug=True, host="0.0.0.0", dev_tools_ui=None)
