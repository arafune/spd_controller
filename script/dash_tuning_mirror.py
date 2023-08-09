#!/usr/bin/env python3
"""Dash based application for tunig mirror and flipper"""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, State, ctx, dcc, html

import spd_controller.newport.picomotor8742 as picomotor8742
import spd_controller.thorlabs.mff101 as mff101

from spd_controller.newport.picomotor8742 import Axis

external_stylesheets = [dbc.themes.MATERIA]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Mirror tuning",
    update_title="",
    suppress_callback_exceptions=True,
)

# ---------- Layout


def flipper_component(id: int):
    """Flipper flipper_component

    Parameters
    ----------
    id : int
        1 or 2
    """
    return html.Div(
        [
            html.H3(
                f"Flipper {id}", style={"marginLeft": "2em", "display": "inline-block"}
            ),
            dbc.Button(
                "Flip {}!".format(id),
                size="large",
                color="primary",
                id=f"flip{id}",
                style={
                    "display": "inline-block",
                    "align-items": "center",
                    "justify-content": "center",
                    "marginLeft": "5%",
                    "marginBottom": ".3em",
                    "marginTop": ".3em",
                },
            ),
        ],
        id=f"flipper{id}",
        style={
            "margin": "2em",
            "border-style": "solid",
            "border-radius": "10pt",
            "border-color": "green",
        },
    )


def mirror_component(id: int):
    """Mirror flipper_component

    Parameters
    ----------
    id: int
        1 or 3
    """
    return html.Div(
        [
            html.H3(f"Mirror {id}ω", style={"marginLeft": "2em", "marginTop": "0.3em"}),

            html.Div(
                [
                    daq.LEDDisplay(
                        value="0",
                        color="red",
                        id=f"position_{id}omega",
                        size=24,
                        style={"marginLeft": "1em"},
                    ),
                    dbc.Button(
                        "◀",
                        color="primary",
                        size="sm",
                        style={"marginLeft": "2em"},
                        id=f"left_{id}omega",
                    ),
                    dbc.Button(
                        "■",
                        color="primary",
                        size="sm",
                        id=f"stop_{id}omega",
                    ),
                    dbc.Button(
                        "▶",
                        color="primary",
                        size="sm",
                        id=f"right_{id}omega",
                    ),
                    dbc.Tooltip(
                        "Anti-clockwise rotation indefinitely",
                        target=f"left_{id}omega",
                        placement="top",
                    ),
                    dbc.Tooltip(
                        "Clockwise rotation indefiniteely",
                        target=f"right_{id}omega",
                        placement="top",
                    ),
                    dbc.Tooltip(
                        "Stop rotating", target=f"stop_{id}omega", placement="top"
                    ),
                ],
                style={"display": "inline-block", "width": "30%"},
            ),
            html.Div(
                [
                    dbc.DropdownMenu(
                        label="Velocity",
                        children=[
                            dbc.DropdownMenuItem(
                                "Max", id=f"velocity_{id}omega_max", n_clicks=0
                            ),
                            dbc.DropdownMenuItem(
                                "Middle", id=f"velocity_{id}omega_middle", n_clicks=0
                            ),
                            dbc.DropdownMenuItem(
                                "Low", id=f"velocity_{id}omega_low", n_clicks=0
                            ),
                        ],
                        className="mb-3",
                        size="sm",
                        id=f"velocity_{id}omega",
                        style={"display": "inline-block"},
                    ),
                    dbc.Tooltip(
                        "Max: 2000 (step/s), Middle: 200, Low:20",
                        target=f"velocity_{id}omega",
                        placement="top",
                    ),
                    html.P(
                        children="Max",
                        id=f"current_velocity_{id}omega",
                        style={"display": "inline-block", "marginLeft": "1em"},
                    ),
                ],
                style={"display": "inline-block", "marginLeft": "2em"},
            ),
            html.Div(
                [
                    dbc.Input(
                        type="number",
                        min=-1000,
                        max=1000,
                        step=1,
                        placeholder="Input steps from here",
                        inputmode="numeric",
                        debounce=True,
                        disabled=False,
                        value=0,
                        id=f"move_{id}omega",
                        size="md",
                        style={
                            "display": "inline-block",
                            "width": "10em",
                        },
                    ),
                    dbc.Button(
                        "Move",
                        color="primary",
                        id=f"move_start_{id}omega",
                        style={
                            "display": "inline-block",
                            "marginLeft": "1em",
                        },
                    ),
                ],
                style={
                    "text-align": "center",
                    "marginBottom": ".3em",
                },
            ),
        ],
        id=f"mirror{id}",
        style={
            "border-style": "solid",
            "border-radius": "10pt",
            "border-color": "red",
            "margin": "2em",
        },
    )


app.layout = html.Article(
    children=[
        html.H1("Tuning Mirrors", style={"text-align": "center"}),
        dcc.Interval(id="realtime_interval", interval=1000),
        html.Div(
            [
                flipper_component(1),
                flipper_component(2),
            ],
            style={"display": "inline-block", "width": "50%", "verticalAlign": "top"},
        ),
        html.Div(
            [
                mirror_component(3),
                mirror_component(1),
            ],
            style={"display": "inline-block", "width": "50%", "verticalAlign": "top"},
        ),
    ],
    lang="english",
)

# Callback
# ---------- Flipper Button


def flipbutton(id, n_clicks) -> dict[str, str]:
    """Base of the callback function for flipbutton1

    Parameters
    --------------
    n_clicks: int
        number of clicks

    Returns
    -------
    dict [str, str]
        css style of the border
    """
    if id == 1:
        flipper = flipper1
    elif id == 2:
        flipper = flipper2
    else:
        raise RuntimeError("We have only 2 flippers")
    if n_clicks is not None:
        flipper.flip()
    if flipper.position() in (1, 18):
        return {
            "margin": "2em",
            "border-style": "solid",
            "border-radius": "10pt",
            "border-color": "green",
        }
    return {
        "margin": "2em",
        "border-style": "solid",
        "border-radius": "10pt",
        "border-color": "blue",
    }


@app.callback(Output("flipper1", "style"), Input("flip1", "n_clicks"))
def flipbutton1(n_clicks: int) -> dict[str, str]:
    """Flip the flipper1

    Parameters
    ----------
    n_clicks : int
        number of clicks of the button

    Returns
    -------
    dict[str, str]
        css style of the border
    """
    return flipbutton(1, n_clicks)


@app.callback(Output("flipper2", "style"), Input("flip2", "n_clicks"))
def flipbutton2(n_clicks: int) -> dict[str, str]:
    """Flip the flipper2

    Parameters
    ----------
    n_clicks : int
        number of clicks of the button

    Returns
    -------
    dict[str, str]
        css style of the border
    """
    return flipbutton(2, n_clicks)


# ----------- Callback: Mirror


def move_mirror_indefinitely(axis: Axis, action: str) -> bool:
    """Move mirror indefinitely

    Parameters
    ----------
    axis: int
        Axis number
    action: str
        "left", "right", or other (= "stop")

    Returns
    -------
    bool
        Return true/false to set "disable" property of the dash component
    """
    if action == "left":
        picomotor.move_indefinitely(axis, False)
        return True
    elif action == "right":
        picomotor.move_indefinitely(axis, True)
        return True
    else:
        picomotor.force_stop(axis)
        return False


@app.callback(
    Output("move_start_3omega", "disabled"),
    Input("right_3omega", "n_clicks"),
    Input("left_3omega", "n_clicks"),
    Input("stop_3omega", "n_clicks"),
)
def move_3omega_mirror_indefinitely(
    right_button: int, left_button: int, stop_button: int
):
    button_clicked = ctx.triggered_id
    if button_clicked == "right_3omega":
        return move_mirror_indefinitely(1, "right")
    elif button_clicked == "left_3omega":
        return move_mirror_indefinitely(1, "left")
    else:
        return move_mirror_indefinitely(1, "stop")


@app.callback(
    Output("move_start_1omega", "disabled"),
    Input("right_1omega", "n_clicks"),
    Input("left_1omega", "n_clicks"),
    Input("stop_1omega", "n_clicks"),
)
def move_1omega_mirror_indefinitely(
    right_button: int, left_button: int, stop_button: int
):
    button_clicked = ctx.triggered_id
    if button_clicked == "right_1omega":
        return move_mirror_indefinitely(2, "right")
    elif button_clicked == "left_1omega":
        return move_mirror_indefinitely(2, "left")
    else:
        return move_mirror_indefinitely(2, "stop")


@app.callback(
    Output("current_velocity_3omega", "children"),
    Input("velocity_3omega_max", "n_clicks"),
    Input("velocity_3omega_middle", "n_clicks"),
    Input("velocity_3omega_low", "n_clicks"),
)
def change_3omega_mirror_velocity(max_speed, middle_speed, low_speed) -> str:
    selected_item = ctx.triggered_id
    if selected_item == "velocity_3omega_max":
        picomotor.set_velocity(1, 2000)
        return "Max"
    elif selected_item == "velocity_3omega_middle":
        picomotor.set_velocity(1, 200)
        return "Middle"
    else:
        picomotor.set_velocity(1, 20)
        return "Low"


@app.callback(
    Output("current_velocity_1omega", "children"),
    Input("velocity_1omega_max", "n_clicks"),
    Input("velocity_1omega_middle", "n_clicks"),
    Input("velocity_1omega_low", "n_clicks"),
)
def change_1omega_mirror_velocity(max_speed, middle_speed, low_speed) -> str:
    selected_item = ctx.triggered_id
    if selected_item == "velocity_1omega_max":
        picomotor.set_velocity(2, 2000)
        return "Max"

    elif selected_item == "velocity_1omega_middle":
        picomotor.set_velocity(2, 200)
        return "Middle"
    else:
        picomotor.set_velocity(1, 20)
        return "Low"


def move_start(axis: int, distance: int) -> tuple[bool, bool, bool]:
    """Function for move_start_button

    Parameters
    -------------
    axis: int
        Axis number
    distance: int
        Relative distance(step)

    Returns
    --------
    tuple[bool, bool, bool]
       value for "disabled" property of button
    """
    picomotor.move_rel(axis, distance)
    return False, False, False


@app.callback(
    Output("left_3omega", "disabled"),
    Output("stop_3omega", "disabled"),
    Output("right_3omega", "disabled"),
    State("move_3omega", "value"),
    Input("move_start_3omega", "n_clicks"),
)
def move_start_3omega(distance: int, n_clicks: int) -> tuple[bool, bool, bool]:
    """
    Trigger of 3ω mirror moving

    Parameters
    ----------
    distance: int
        number of steps
    n_clicks
        number of clicks of the dash buttom

    Returns
    -------
    tuple[bool, bool, bool]
        "disable" property of the dash component
    """
    if n_clicks is not None:
        return move_start(1, distance)
    return True, True, True


@app.callback(
    Output("left_1omega", "disabled"),
    Output("stop_1omega", "disabled"),
    Output("right_1omega", "disabled"),
    State("move_1omega", "value"),
    Input("move_start_1omega", "n_clicks"),
)
def move_start_1omega(distance: int, n_clicks: int) -> tuple[bool, bool, bool]:
    """Trigger of 3ω mirror moving


    Parameters
    ----------
    distance
        number of steps
    n_clicks
        number of clicks of the dash buttom

    Returns
    -------
    tuple[bool, bool, bool]
        "disable" property of the dash component
    """
    if n_clicks is not None:
        return move_start(2, distance)
    return True, True, True


@app.callback(
    Output("position_3omega", "value"),
    Output("position_1omega", "value"),
    Input("realtime_interval", "n_intervals"),
)
def update_mirror_position(n_intervals: int) -> tuple[int, int]:
    """Return the current mirror tilt


    Parameters
    ----------
    n_intervals: int
        incremented by dash

    Returns
    -------
    tuple[int, int]
        step of the actuator
    """
    if n_intervals is not None:
        mirror_position1 = picomotor.position(1)
        mirror_position2 = picomotor.position(2)
        return mirror_position1, mirror_position2
    return 0, 0


# --Main

if __name__ == "__main__":
    flipper1 = mff101.MFF101("37003548")
    flipper2 = mff101.MFF101("37003278")
    picomotor = picomotor8742.Picomotor8742(host="144.213.126.101")
    picomotor.connect()
    app.run_server(debug=True, host="0.0.0.0", dev_tools_ui=None)
