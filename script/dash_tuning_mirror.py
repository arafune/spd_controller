#!/usr/bin/env python3
"""Dash based application for tunig mirror and flipper"""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, State, html

import spd_controller.newport.picomotor8742 as picomotor8742
import spd_controller.thorlabs.mff101 as mff101

external_stylesheets = [dbc.themes.MATERIA]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Mirror tuning",
    update_title="",
    suppress_callback_exceptions=True,
)


def flipper_component(id: int):
    """Flipper flipper_component

    Parameters
    ------------
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
    -------------
    id: int
        1 or 3
    """
    return html.Div(
        [
            html.H3(f"Mirrror {id}ω", style={"marginLeft": "2em"}),
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
                "stop",
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
                            "display": "incline-block",
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


# ---------- Flipper Button


def flipbutton_n(id, n_clicks):
    """Call back function for flipbutton1

    Parameters
    --------------
    n_clicks: int
        number of clicks

    Returns
    -------
    dict [str, str]
        style of the border
    """
    if n_clicks > 0:
        setattr(f"flipper{id}", "flip", None)
    if getattr(f"flipper{id}", "position") == 1:
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


@app.callback(Output("flipper1", "style"), Input("flipper1", "n_clicks"))
def flipbutton1(n_clicks):
    return flipbutton_n(1, n_clicks)


@app.callback(Output("flipper2", "style"), Input("flipper2", "n_clicks"))
def flipbutton2(n_clicks):
    return flipbutton_n(2, n_clicks)


# ----------- Callback: Mirror


def left_mirror(axis: int, n_clicks: int):
    if n_clicks > 0 and picomotor.check_stop(axis):
        picomotor.move_indefinitely(axis, False)
    return True


@app.callback(Output("move_3omega", "disabled"), Input("left_3omega", "n_clicks"))
def left_mirror3omega(n_clicks: int):
    return left_mirror(1, n_clicks)


@app.callback(Output("move_1omega", "disabled"), Input("left_1omega", "n_clicks"))
def left_mirror1omega(n_clicks: int):
    return left_mirror(2, n_clicks)


def right_mirror(axis: int, n_clicks: int):
    if n_clicks > 0 and picomotor.check_stop(axis):
        picomotor.move_indefinitely(axis, True)
    return True


@app.callback(Output("move_3omega", "disabled"), Input("right_3omega", "n_clicks"))
def right_mirror3omega(n_clicks: int):
    return right_mirror(1, n_clicks)


@app.callback(Output("move_1omega", "disabled"), Input("right_1omega", "n_clicks"))
def right_mirror1omega(n_clicks: int):
    return right_mirror(2, n_clicks)


def stop_mirror(axis: int, n_clicks: int):
    if n_clicks > 0:
        picomotor.force_stop(axis)
    return False


@app.callback(Output("move_3omega", "disabled"), Input("stop_3omega", "n_clicks"))
def stop_mirror3omega(n_clicks: int):
    return stop_mirror(1, n_clicks)


@app.callback(Output("move_1omega", "disabled"), Input("stop_1omega", "n_clicks"))
def stop_mirror1omega(n_clicks: int):
    return stop_mirror(2, n_clicks)


def move_by_value(distance: int) -> tuple[bool, bool, bool]:
    """Function for Input of distance

    Parameters
    -------------
    distance: int
        Relative distance(step)

    Returns
    --------
    tuple[bool, bool, bool]
       value for "disabled" property of button
    """
    assert isinstance(distance, int)
    return True, True, True


@app.callback(
    Output("left_3omega", "disabled"),
    Output("stop_3omega", "disabled"),
    Output("right_3omega", "disabled"),
    Input("move_3omega", "value"),
)
def move_by_value_3omega(distance: int) -> tuple[bool, bool, bool]:
    return move_by_value(distance)


@app.callback(
    Output("left_1omega", "disabled"),
    Output("stop_1omega", "disabled"),
    Output("right_1omega", "disabled"),
    Input("move_1omega", "value"),
)
def move_by_value_1omega(distance: int) -> tuple[bool, bool, bool]:
    return move_by_value(distance)


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
    if n_clicks > 0:
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
    if n_clicks > 0:
        return move_start(2, distance)
    return True, True, True


@app.callback(
    Output("position_3omega", "value"),
    Output("position_1omega", "value"),
    Input("realtime_interval", "n_intervals"),
)
def update_mirror_position(n_intervals: int) -> tuple[int, int]:
    if n_intervals > 0:
        mirror_position1 = picomotor.position(1)
        mirror_position2 = picomotor.position(2)
        return mirror_position1, mirror_position2
    return 0, 0


if __name__ == "__main__":
    flipper1 = mff101.MFF101("serial1")
    flipper2 = mff101.MFF101("serial2")
    picomotor = picomotor8742.Picomotor8742("144.213.126.101")
    picomotor.connect()
    app.run_server(debug=True, host="0.0.0.0")
