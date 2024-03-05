#!/usr/bin/env python3
"""Dash based application for tuning mirror and flipper."""

import argparse
from typing import Literal
from logging import DEBUG, INFO, Formatter, Logger, StreamHandler, getLogger
from enum import Enum

import dash
import dash_bootstrap_components as dbc
from _dash_tuning_mirror_layout import (
    flipper1_button,
    flipper2_button,
    mirror_component,
)
from dash import Input, Output, State, ctx, dcc, html

from spd_controller.newport.picomotor8742 import Axis, MockPicomoter8742, Picomotor8742
from spd_controller.thorlabs.mff101 import MFF101, MockMFF101

external_stylesheets = [dbc.themes.MATERIA]

LOGLEVEL = (DEBUG, INFO)[1]
logger: Logger = getLogger(__name__)
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
formatter: Formatter = Formatter(fmt)
handler = StreamHandler()
handler.setLevel(LOGLEVEL)
logger.setLevel(LOGLEVEL)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


class AXIS(Enum):
    h_3omega = 1
    h_omega = 2
    v_3omega = 3
    v_omega = 4


FlipperID = Literal[1, 2]

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


def flipbutton(
    id: FlipperID,
    n_clicks: int,
) -> dict[str, str]:
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


@app.callback(
    Output("flipper_1", "style"),
    #
    Input("flipper_1", "n_clicks"),
)
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


@app.callback(
    Output("flipper_2", "style"),
    #
    Input("flipper_2", "n_clicks"),
)
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


def move_mirror_indefinitely(
    axis: Axis,
    action: str,
) -> bool:
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


# --------


def move_start(
    axis: Literal[1, 2, 3, 4],
    distance: int,
) -> tuple[bool, bool, bool, bool, bool]:
    picomotor.move_rel(axis, distance)
    return False, False, False, False, False


@app.callback(
    Output("right_3", "disabled"),
    Output("left_3", "disabled"),
    Output("up_3", "disabled"),
    Output("down_3", "disabled"),
    Output("stop_3", "disabled"),
    #
    State("movement_3", "value"),
    Input("move_h_3", "n_clicks"),
    Input("move_v_3", "n_clicks"),
)
def move_3omega(
    distance: int,
    n_clicks_h: int | None,
    n_clicks_v: int | None,
) -> tuple[bool, bool, bool, bool, bool]:
    logger.debug(f"n_clics_h 3ω {n_clicks_h}")
    logger.debug(f"n_clics_v 3ω {n_clicks_v}")
    button_clicked = ctx.triggered_id
    if button_clicked == "move_h_3":
        return move_start(AXIS.h_3omega.value, distance)
    elif button_clicked == "move_v_3":
        return move_start(AXIS.v_3omega.value, distance)
    return True, True, True, True, True


@app.callback(
    Output("right_1", "disabled"),
    Output("left_1", "disabled"),
    Output("up_1", "disabled"),
    Output("down_1", "disabled"),
    Output("stop_1", "disabled"),
    #
    State("movement_1", "value"),
    Input("move_h_1", "n_clicks"),
    Input("move_v_1", "n_clicks"),
)
def move_1omega(
    distance: int,
    n_clicks_h: int | None,
    n_clicks_v: int | None,
) -> tuple[bool, bool, bool, bool, bool]:
    logger.debug(f"n_clics_h ω {n_clicks_h}")
    logger.debug(f"n_clics_v ω {n_clicks_v}")
    button_clicked = ctx.triggered_id
    if button_clicked == "move_h_1":
        return move_start(AXIS.h_omega.value, distance)
    elif button_clicked == "move_v_1":
        return move_start(AXIS.v_omega.value, distance)
    return True, True, True, True, True


@app.callback(
    Output("move_h_3", "disabled"),
    Output("move_v_3", "disabled"),
    #
    Input("right_3", "n_clicks"),
    Input("left_3", "n_clicks"),
    Input("up_3", "n_clicks"),
    Input("down_3", "n_clicks"),
    Input("stop_3", "n_clicks"),
)
def move_3omega_mirror_indefinitely(
    right_button: int,
    left_button: int,
    up_button: int,
    down_button: int,
    stop_button: int,
) -> tuple[bool, bool]:
    logger.debug(f"right_button 3ω {right_button}")
    logger.debug(f"left_button 3ω {left_button}")
    logger.debug(f"up_button 3ω {up_button}")
    logger.debug(f"down_button 3ω {down_button}")
    logger.debug(f"stop_button 3ω {stop_button}")
    button_clicked = ctx.triggered_id
    if button_clicked == "right_3":
        ret_bool = move_mirror_indefinitely(AXIS.h_3omega.value, "ccw")
        return ret_bool, ret_bool
    elif button_clicked == "left_3":
        ret_bool = move_mirror_indefinitely(AXIS.h_3omega.value, "cw")
        return ret_bool, ret_bool
    elif button_clicked == "up_3":
        ret_bool = move_mirror_indefinitely(AXIS.v_3omega.value, "ccw")
        return ret_bool, ret_bool
    elif button_clicked == "down_3":
        ret_bool = move_mirror_indefinitely(AXIS.v_3omega.value, "cw")
        return ret_bool, ret_bool
    else:
        return move_mirror_indefinitely(
            AXIS.h_3omega.value,
            "stop",
        ), move_mirror_indefinitely(
            AXIS.v_3omega.value,
            "stop",
        )


@app.callback(
    Output("move_h_1", "disabled"),
    Output("move_v_1", "disabled"),
    #
    Input("right_1", "n_clicks"),
    Input("left_1", "n_clicks"),
    Input("up_1", "n_clicks"),
    Input("down_1", "n_clicks"),
    Input("stop_1", "n_clicks"),
)
def move_1omega_mirror_indefinitely(
    right_button: int,
    left_button: int,
    up_button: int,
    down_button: int,
    stop_button: int,
) -> tuple[bool, bool]:
    logger.debug(f"right_button ω {right_button}")
    logger.debug(f"left_button ω {left_button}")
    logger.debug(f"up_button ω {up_button}")
    logger.debug(f"down_button ω {down_button}")
    logger.debug(f"stop_button ω {stop_button}")
    button_clicked = ctx.triggered_id
    if button_clicked == "right_1":
        ret_bool = move_mirror_indefinitely(AXIS.h_omega.value, "ccw")
        return ret_bool, ret_bool
    elif button_clicked == "left_1":
        ret_bool = move_mirror_indefinitely(AXIS.h_omega.value, "cw")
        return ret_bool, ret_bool
    elif button_clicked == "up_1":
        ret_bool = move_mirror_indefinitely(AXIS.v_omega.value, "ccw")
        return ret_bool, ret_bool
    elif button_clicked == "down_1":
        ret_bool = move_mirror_indefinitely(AXIS.v_omega.value, "cw")
        return ret_bool, ret_bool
    else:
        return move_mirror_indefinitely(
            AXIS.h_omega.value, "stop"
        ), move_mirror_indefinitely(AXIS.v_omega.value, "stop")


@app.callback(
    Output("current_velocity_3", "children"),
    #
    Input("velocity_3_max", "n_clicks"),
    Input("velocity_3_middle", "n_clicks"),
    Input("velocity_3_min", "n_clicks"),
)
def change_3omega_mirror_velocity(
    max_speed: int,
    middle_speed: int,
    minimum_speed: int,
) -> str:
    logger.debug(f"max_speed button 3ω {max_speed}")
    logger.debug(f"middle_speed button 3ω {middle_speed}")
    logger.debug(f"minimu_speed button 3ω {minimum_speed}")
    selected_item = ctx.triggered_id
    if selected_item == "velocity_3_max":
        picomotor.set_velocity(AXIS.h_3omega.value, 2000)
        picomotor.set_velocity(AXIS.v_3omega.value, 2000)
        return "Max speed"
    elif selected_item == "velocity_3_middle":
        picomotor.set_velocity(AXIS.h_3omega.value, 200)
        picomotor.set_velocity(AXIS.v_3omega.value, 200)
        return "Middle speed"
    else:
        picomotor.set_velocity(AXIS.h_3omega.value, 20)
        picomotor.set_velocity(AXIS.v_3omega.value, 20)
        return "Low speed"


@app.callback(
    Output("current_velocity_1", "children"),
    #
    Input("velocity_1_max", "n_clicks"),
    Input("velocity_1_middle", "n_clicks"),
    Input("velocity_1_min", "n_clicks"),
)
def change_1omega_mirror_velocity(
    max_speed: int,
    middle_speed: int,
    minimum_speed: int,
) -> str:
    logger.debug(f"max_speed button ω {max_speed}")
    logger.debug(f"middle_speed button ω {middle_speed}")
    logger.debug(f"minimu_speed button ω {minimum_speed}")
    selected_item = ctx.triggered_id
    if selected_item == "velocity_1_max":
        picomotor.set_velocity(AXIS.h_omega.value, 2000)
        picomotor.set_velocity(AXIS.v_omega.value, 2000)
        return "Max speed"
    elif selected_item == "velocity_1_middle":
        picomotor.set_velocity(AXIS.h_omega.value, 200)
        picomotor.set_velocity(AXIS.v_omega.value, 200)
        return "Middle speed"
    else:
        picomotor.set_velocity(AXIS.h_omega.value, 20)
        picomotor.set_velocity(AXIS.v_omega.value, 20)
        return "Low speed"


@app.callback(
    Output("position_h_3ω", "value"),
    Output("position_v_3ω", "value"),
    Output("position_h_1ω", "value"),
    Output("position_v_1ω", "value"),
    #
    Input("realtime_interval", "n_intervals"),
)
def update_mirror_positon(n_intervals: int | None) -> tuple[int, int, int, int]:
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
        mirror_position2 = picomotor.position(AXIS.v_3omega.value)
        mirror_position3 = picomotor.position(AXIS.h_omega.value)
        mirror_position4 = picomotor.position(AXIS.v_omega.value)
        return mirror_position1, mirror_position2, mirror_position3, mirror_position4
    return 0, 0, 0, 0


# ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--use_mock", action="store_true", help="Use Mock for check", default=False
    )
    args = parser.parse_args()
    idcodes = ("37003548", "37003278")
    host_address = "144.213.126.101"
    if args.use_mock:
        LOGLEVEL = DEBUG
        logger.debug("Use Mock Mode")
        flipper1: MFF101 | MockMFF101 = MockMFF101(str(idcodes[0]))
        flipper2: MFF101 | MockMFF101 = MockMFF101(str(idcodes[1]))
        logger.debug(f"Use MockMFF101 for {idcodes[0]}")
        logger.debug(f"Use MockMFF101 for {idcodes[1]}")
        picomotor: Picomotor8742 | MockPicomoter8742 = MockPicomoter8742()
        logger.debug("Use MociPicomoter8742")
    else:
        flipper1 = MFF101(str(idcodes[0]))
        if not flipper1.ready:
            flipper1 = MockMFF101(str(idcodes[0]))
            logger.debug(f"Use MockMFF101 for {idcodes[0]}")
        flipper2 = MFF101(str(idcodes[1]))
        if not flipper2.ready:
            flipper2 = MockMFF101(str(idcodes[1]))
        #
        picomotor = Picomotor8742(host=host_address)
        try:
            picomotor.connect()
        except (TimeoutError, OSError):
            logger.debug("Use MockPicomoter8742")
            picomotor = MockPicomoter8742()
    app.run_server(debug=True, host="0.0.0.0", dev_tools_ui=None)
