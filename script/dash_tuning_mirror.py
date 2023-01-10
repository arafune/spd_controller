#!/usr/bin/env python3
"""Dash based application for tunig mirror and flipper"""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, State, dcc, html

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
            html.H2("Flipper {}".format(id), style={"marginLeft": "2em"}),
            dbc.Button(
                "Flip {}!".format(id),
                size="large",
                color="primary",
                id="flipper{}".format(id),
                style={
                    "marginLeft": "10em",
                    "marginBottom": ".3em",
                },
            ),
        ],
        style={
            "margin": "2em",
            "border-style": "solid",
            "border-radius": "20pt",
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
    html.Div(
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
                        type="relative move",
                        step=1,
                        placeholder="Input steps from here",
                        inputmode="numeric",
                        id=f"move_{id}omega",
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
        style={
            "border-style": "solid",
            "border-radius": "20pt",
            "border-color": "red",
            "margin": "2em",
        },
    )


app.layout = html.Article(
    children=[
        html.H1("Tuning Mirrors", style={"text-align": "center"}),
        html.Div(
            [
                # html.H2("Flipper", style={"text-align": "center"}),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2("Flipper 1", style={"marginLeft": "2em"}),
                                dbc.Button(
                                    "Flip 1!",
                                    size="large",
                                    color="primary",
                                    id="flipper1",
                                    style={
                                        "marginLeft": "10em",
                                        "marginBottom": ".3em",
                                    },
                                ),
                            ],
                            style={
                                "margin": "2em",
                                "border-style": "solid",
                                "border-radius": "20pt",
                                "border-color": "green",
                            },
                        ),
                        html.Div(
                            [
                                html.H2(
                                    "Flipper 2",
                                    style={"marginLeft": "2em"},
                                ),
                                dbc.Button(
                                    "Flip 2!",
                                    size="large",
                                    color="primary",
                                    id="filpper2",
                                    style={
                                        "marginLeft": "10em",
                                        "marginBottom": ".3em",
                                    },
                                ),
                            ],
                            style={
                                "margin": "2em",
                                "border-style": "solid",
                                "border-radius": "20pt",
                                "border-color": "green",
                            },
                        ),
                    ]
                ),
            ],
            style={"display": "inline-block", "width": "50%", "verticalAlign": "top"},
        ),
        html.Div(
            [
                # html.H2("Mirror", style={"text-align": "center"}),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3("Mirrror 3ω", style={"marginLeft": "2em"}),
                                daq.LEDDisplay(
                                    value="0",
                                    color="red",
                                    id="position_3omega",
                                    size=24,
                                    style={"marginLeft": "1em"},
                                ),
                                dbc.Button(
                                    "◀",
                                    color="primary",
                                    size="sm",
                                    style={"marginLeft": "2em"},
                                    id="left_3omega",
                                ),
                                dbc.Button(
                                    "stop",
                                    color="primary",
                                    size="sm",
                                    id="stop_3omega",
                                ),
                                dbc.Button(
                                    "▶",
                                    color="primary",
                                    size="sm",
                                    id="right_3omega",
                                ),
                                html.Div(
                                    [
                                        dbc.Input(
                                            type="relative move",
                                            step=1,
                                            placeholder="Input steps from here",
                                            inputmode="numeric",
                                            id="move_3omega",
                                            style={
                                                "display": "inline-block",
                                                "width": "10em",
                                            },
                                        ),
                                        dbc.Button(
                                            "Move",
                                            color="primary",
                                            id="move_start_3omega",
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
                            style={
                                "border-style": "solid",
                                "border-radius": "20pt",
                                "border-color": "red",
                                "margin": "2em",
                            },
                        ),
                        html.Div(
                            [
                                html.H3("Mirror ω", style={"marginLeft": "2em"}),
                                daq.LEDDisplay(
                                    value="0",
                                    color="red",
                                    id="position_omega",
                                    size=24,
                                    style={"marginLeft": "1em"},
                                ),
                                dbc.Button(
                                    "◀",
                                    color="primary",
                                    size="sm",
                                    style={"marginLeft": "2em"},
                                    id="left_omega",
                                ),
                                dbc.Button(
                                    "stop",
                                    color="primary",
                                    size="sm",
                                    id="stop_omega",
                                ),
                                dbc.Button(
                                    "▶",
                                    color="primary",
                                    size="sm",
                                    id="right_omega",
                                ),
                                html.Div(
                                    [
                                        dbc.Input(
                                            type="relative move",
                                            placeholder="Input steps from here",
                                            step=1,
                                            inputmode="numeric",
                                            id="move_omega",
                                            style={
                                                "display": "inline-block",
                                                "width": "10em",
                                            },
                                        ),
                                        dbc.Button(
                                            "Move",
                                            color="primary",
                                            id="move_start_omega",
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
                            style={
                                "border-style": "solid",
                                "border-radius": "20pt",
                                "border-color": "red",
                                "margin": "2em",
                            },
                        ),
                    ]
                ),
            ],
            style={"display": "inline-block", "width": "50%", "verticalAlign": "top"},
        ),
    ],
    lang="english",
)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
