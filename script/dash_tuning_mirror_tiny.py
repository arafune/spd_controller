#!/usr/bin/env python3
"""Dash based application for tunig mirror"""

from __future__ import annotations

from logging import INFO, Formatter, Logger, StreamHandler, getLogger
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, State, ctx, dcc, html
from enum import Enum


from spd_controller.newport.picomotor8742 import Axis, Picomotor8742, MockPicomoter8742

LOGLEVEL = INFO
logger: Logger = getLogger(__name__)
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
formatter: Formatter = Formatter(fmt)
handler = StreamHandler()
handler.setLevel(LOGLEVEL)
logger.setLevel(LOGLEVEL)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


external_stylesheets = [dbc.themes.MATERIA]


class AXIS(Enum):
    h_3omega = 1
    h_omega = 2


app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Mirror tuning",
    update_title="",
    suppress_callback_exceptions=True,
)

# ---------- Layout


def mirror_component(id: int):
    """Mirror component

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
                mirror_component(3),
                mirror_component(1),
            ],
            style={"display": "inline-block", "width": "50%", "verticalAlign": "top"},
        ),
    ],
    lang="english",
)

# Callback

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
        picomotor.move_indefinitely(axis, positive=False)
        return True
    elif action == "right":
        picomotor.move_indefinitely(axis, positive=True)
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
    logger.debug(f"right button 3omega: {right_button}")
    logger.debug(f"left button 3omega: {left_button}")
    logger.debug(f"stop button 3omega: {stop_button}")
    button_clicked = ctx.triggered_id
    if button_clicked == "right_3omega":
        return move_mirror_indefinitely(AXIS.h_3omega.value, "right")
    elif button_clicked == "left_3omega":
        return move_mirror_indefinitely(AXIS.h_3omega.value, "left")
    else:
        return move_mirror_indefinitely(AXIS.h_3omega.value, "stop")


@app.callback(
    Output("move_start_1omega", "disabled"),
    Input("right_1omega", "n_clicks"),
    Input("left_1omega", "n_clicks"),
    Input("stop_1omega", "n_clicks"),
)
def move_1omega_mirror_indefinitely(
    right_button: int, left_button: int, stop_button: int
):
    logger.debug(f"right button omega: {right_button}")
    logger.debug(f"left button omega: {left_button}")
    logger.debug(f"stop button omega: {stop_button}")
    button_clicked = ctx.triggered_id
    if button_clicked == "right_1omega":
        return move_mirror_indefinitely(AXIS.h_omega.value, "right")
    elif button_clicked == "left_1omega":
        return move_mirror_indefinitely(AXIS.h_omega.value, "left")
    else:
        return move_mirror_indefinitely(AXIS.h_omega.value, "stop")


@app.callback(
    Output("current_velocity_3omega", "children"),
    Input("velocity_3omega_max", "n_clicks"),
    Input("velocity_3omega_middle", "n_clicks"),
    Input("velocity_3omega_low", "n_clicks"),
)
def change_3omega_mirror_velocity(max_speed, middle_speed, low_speed) -> str:
    logger.debug(f"max speed button 3omega: {max_speed}")
    logger.debug(f"middle speed button 3omega: {middle_speed}")
    logger.debug(f"low speed button 3omega: {low_speed}")
    selected_item = ctx.triggered_id
    if selected_item == "velocity_3omega_max":
        picomotor.set_velocity(AXIS.h_3omega.value, 2000)
        return "Max"
    elif selected_item == "velocity_3omega_middle":
        picomotor.set_velocity(AXIS.h_3omega.value, 200)
        return "Middle"
    else:
        picomotor.set_velocity(AXIS.h_3omega.value, 20)
        return "Low"


@app.callback(
    Output("current_velocity_1omega", "children"),
    Input("velocity_1omega_max", "n_clicks"),
    Input("velocity_1omega_middle", "n_clicks"),
    Input("velocity_1omega_low", "n_clicks"),
)
def change_1omega_mirror_velocity(max_speed, middle_speed, low_speed) -> str:
    logger.debug(f"max speed button omega: {max_speed}")
    logger.debug(f"middle speed button omega: {middle_speed}")
    logger.debug(f"low speed button omega: {low_speed}")
    selected_item = ctx.triggered_id
    if selected_item == "velocity_1omega_max":
        picomotor.set_velocity(AXIS.h_omega.value, 2000)
        return "Max"

    elif selected_item == "velocity_1omega_middle":
        picomotor.set_velocity(AXIS.h_omega.value, 200)
        return "Middle"
    else:
        picomotor.set_velocity(AXIS.h_omega.value, 20)
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
def move_start_3omega(distance: int, n_clicks: int | None) -> tuple[bool, bool, bool]:
    """
    Trigger of 3ω mirror moving

    Parameters
    ----------
    distance: int
        number of steps
    n_clicks
        number of clicks of the dash button

    Returns
    -------
    tuple[bool, bool, bool]
        "disable" property of the dash component
    """
    if n_clicks is not None:
        return move_start(AXIS.h_3omega.value, distance)
    return True, True, True


@app.callback(
    Output("left_1omega", "disabled"),
    Output("stop_1omega", "disabled"),
    Output("right_1omega", "disabled"),
    State("move_1omega", "value"),
    Input("move_start_1omega", "n_clicks"),
)
def move_start_1omega(distance: int, n_clicks: int | None) -> tuple[bool, bool, bool]:
    """Trigger of 3ω mirror moving


    Parameters
    ----------
    distance
        number of steps
    n_clicks
        number of clicks of the dash button

    Returns
    -------
    tuple[bool, bool, bool]
        "disable" property of the dash component
    """
    if n_clicks is not None:
        return move_start(AXIS.h_omega.value, distance)
    return True, True, True


@app.callback(
    Output("position_3omega", "value"),
    Output("position_1omega", "value"),
    Input("realtime_interval", "n_intervals"),
)
def update_mirror_position(n_intervals: int | None) -> tuple[int, int]:
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
        mirror_position1 = picomotor.position(AXIS.h_3omega.value)
        mirror_position2 = picomotor.position(AXIS.h_omega.value)
        return mirror_position1, mirror_position2
    return 0, 0


# --Main

if __name__ == "__main__":
    picomotor: Picomotor8742 | MockPicomoter8742 = Picomotor8742(host="144.213.126.101")
    try:
        picomotor.connect()
    except (TimeoutError, OSError):
        logger.info("Testing mode")
        picomotor = MockPicomoter8742()
    app.run_server(debug=True, host="0.0.0.0", dev_tools_ui=None)
