#! /usr/bin/env/ python3
"""SC104 and GSC02 controller with Dash
"""
from __future__ import annotations

import dash
import dash_daq as daq
from dash import Input, Output, State, dcc, html

from spd_controller.sigma.gsc02 import GSC02
from spd_controller.sigma.sc104 import SC104

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Delayline & ND filter",
    update_title=None,
)  # remove "Updating..." from title

# Components

delayline_input = dcc.Input(
    id="delayline_position",
    min=0.00,
    max=400.0,
    step=0.01,
    disabled=False,
    debounce=True,
    type="number",
    style={"textAlign": "right", "margin-left": "3%"},
)

ndfilter_input = dcc.Input(
    id="ndfilter_angle",
    min=0,
    max=360,
    debounce=True,
    disabled=False,
    type="number",
    style={"textAlign": "right", "margin-left": "3%"},
)

delay_line_setting = html.Div(
    [
        html.H3("Simple setting"),
        html.P(id="current_position"),
        html.Div(
            [
                html.P(
                    "Delay line mirror position: ",
                    style={"display": "inline-block", "margin-left": "2%"},
                ),
                delayline_input,
            ]
        ),
    ],
    style={"display": "inline-block", "margin-left": "3%"},
)

delay_line_back_forth = html.Div(
    [
        daq.BooleanSwitch(
            id="back_and_forth_mode",
            on=False,
            style={"display": "inline-block"},
            label="Back and Forth mode",
            labelPosition="right",
        ),
        html.Div(
            [
                html.Div(
                    [
                        daq.NumericInput(
                            id="backforth_position1",
                            value=0,
                            max=400,
                            min=0,
                            style={"display": "inline-block"},
                            label="Position 1",
                            labelPosition="top",
                        ),
                    ]
                ),
                html.Div(
                    [
                        daq.NumericInput(
                            id="backforth_position2",
                            value=0,
                            max=400,
                            min=0,
                            style={"display": "inline-block"},
                            label="Position 2",
                            labelPosition="bottom",
                        ),
                    ]
                ),
            ]
        ),
    ],
    style={"display": "inline-block", "margin-right": "5%", "margin-left": "25%"},
)

ndfilter_setting = html.Div(
    [
        html.P(id="current_angle"),
        html.P("SET ND filter angle (degree):  ", style={"display": "inline-block"}),
        ndfilter_input,
    ]
)

#  app.layout

app.layout = html.Div(
    [
        html.Title("Delay line & ND filter contoller"),
        html.H1("Delay line & ND filter contoller", style={"textAlign": "center"}),
        html.Hr(),
        html.H2("Delay line", style={"text-align": "center"}),
        html.Div([delay_line_setting, delay_line_back_forth]),
        html.Hr(),
        html.H2("ND filter", style={"text-align": "center"}),
        ndfilter_setting,
        html.Hr(),
        dcc.Interval(id="intervals", interval=250, max_intervals=-1),
    ]
)


@app.callback(
    Output("delayline_position", "disabled"),
    Output("ndfilter_angle", "disabled"),
    Input("back_and_forth_mode", "on"),
    Input("delayline_position", "value"),
    Input("ndfilter_angle", "value"),
    State("backforth_position1", "value"),
    State("backforth_position2", "value"),
)
def input_value(
    back_and_force_is_on: bool,
    delayline_position: float,
    ndfilter_angle: float,
    backforth_position1: float,
    backforth_position2: float,
) -> tuple[bool, bool]:
    position_now: float | None = s.moving()
    if position_now is None:
        position_now = s.position()
    else:
        position_now = s.force_stop()
    if back_and_force_is_on:
        is_disable_simple_input: bool = True
        if s.check_stop():
            if abs(position_now - backforth_position1) < 0.001:
                s.move_abs(backforth_position2, wait=False)
            else:
                s.move_abs(backforth_position1, wait=False)
    else:  # Simple input mode
        is_disable_simple_input = False
        if s.check_stop() and (delayline_position is not None):
            s.move_abs(delayline_position, wait=False)
        if g.check_stop() and (ndfilter_angle is not None):
            g.set_angle(ndfilter_angle, wait=False)
    return (is_disable_simple_input, is_disable_simple_input)


@app.callback(
    Output("current_position", "children"),
    Output("current_angle", "children"),
    Input("intervals", "n_intervals"),
)
def update(
    n: int,
) -> tuple[str, str]:
    position_now: float | None = s.moving()
    if position_now is None:
        position_now = s.position()
    position_msg: str = "Current Position: {:.4f} mm".format(position_now)
    angle_now: float = g.angle()
    angle_msg: str = "Current Angle: {:.2f} degree".format(angle_now)
    return (
        position_msg,
        angle_msg,
    )


if __name__ == "__main__":
    s: SC104 = SC104()
    g: GSC02 = GSC02()
    app.run_server(debug=False, host="0.0.0.0")
