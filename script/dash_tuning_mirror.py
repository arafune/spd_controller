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

app.layout = html.Article(
    children=[
        html.H1("Tuning Mirrors", style={"text-align": "center"}),
        html.Div(
            [
                # html.H2("Flipper", style={"text-align": "center"}),
                html.Div(
                    [
                        html.H2("Flipper 1"),
                        dbc.Button(
                            "Flip 1!",
                            size="large",
                            color="primary",
                            id="flipper1",
                            style={"marginLeft": "10em"},
                        ),
                        html.H2("Flipper 2", style={"marginTop": "1em"}),
                        dbc.Button(
                            "Flip 2!",
                            size="large",
                            color="primary",
                            id="filpper2",
                            style={"marginLeft": "10em"},
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
                        html.H3("Mirrror 3ω"),
                        daq.LEDDisplay(
                            value="0", color="red", id="position_3omega", size=24
                        ),
                        dbc.Button("◀", color="primary", size="sm"),
                        dbc.Button("stop", color="primary", size="sm"),
                        dbc.Button("▶", color="primary", size="sm"),
                        html.Div(
                            [
                                dbc.Input(
                                    type="relative move",
                                    step=1,
                                    id="move_3omega",
                                    style={"display": "inline-block", "width": "10em"},
                                ),
                                dbc.Button(
                                    "Move",
                                    color="primary",
                                    style={
                                        "display": "incline-block",
                                        "marginLeft": "1em",
                                    },
                                ),
                            ],
                            style={"text-align": "center"},
                        ),
                        html.H3("Mirror ω"),
                        daq.LEDDisplay(
                            value="0", color="red", id="position_omega", size=24
                        ),
                        dbc.Button("◀", color="primary", size="sm"),
                        dbc.Button("stop", color="primary", size="sm"),
                        dbc.Button("▶", color="primary", size="sm"),
                        html.Div(
                            [
                                dbc.Input(
                                    type="relative move",
                                    step=1,
                                    id="move_omega",
                                    style={"display": "inline-block", "width": "10em"},
                                ),
                                dbc.Button(
                                    "Move",
                                    color="primary",
                                    style={
                                        "display": "incline-block",
                                        "marginLeft": "1em",
                                    },
                                ),
                            ],
                            style={"text-align": "center"},
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
