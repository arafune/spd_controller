#!/usr/bin/env python3
"""Qmass spectral data acquisition Web based user interface
    """


from __future__ import annotations

from unittest.mock import MagicMock

import dash
import dash_daq as daq
from dash import Input, Output, State, dcc, html

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# styles

div_style_1_1 = {
    # "margin": "10pt",
    "display": "inline-block",
    # "verticalAlign": "top",
}

div_style_1_2 = {
    # "margin": "10pt",
    "width": "29%",
    "display": "inline-block",
    # "verticalAlign": "top",
}

mode_style = {"margin-top": "0%", "width": "32%", "display": "inline-block"}

massset_style1 = {
    "margin-top": "0%",
    "margin-left": "1%",
    "width": "49%",
    "display": "inline-block",
}

massset_style2 = {"margin-top": "0%", "width": "39%", "display": "inline-block"}

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Q-mass spectroscopy",
    update_title=None,
)  # remove "Updating..." from title


measure_button = html.Div(
    [daq.PowerButton(id="measure_button", on=False, color="red")], style=div_style_1_1
)

filename_input = html.Div(
    [
        dcc.Input(
            id="filename",
            type="text",
            debounce=True,
        ),
    ],
    style=div_style_1_2,
)

filament_selection = html.Div(
    [
        dcc.Dropdown(
            id="filament_selection",
            options=[
                {"label": "No filament", "value": 0},
                {"label": "filament 1", "value": 1},
                {"label": "filament 2", "value": 2},
            ],
            value=0,
            clearable=False,
        )
    ],
    style=div_style_1_2,
)


multiplier_onoff = html.Div(
    [
        daq.BooleanSwitch(
            id="multiplier",
            disabled=True,
            on=False,
            vertical=True,
            color="blue",
        )
    ],
    style=div_style_1_1,
)

mode_selection = html.Div(
    [
        dcc.Dropdown(
            id="mode_selection",
            options=[
                {"label": "Analog mode", "value": "analog_mode"},
                {"label": "Digital mode", "value": "digital_mode"},
                {"label": "Leak check mode", "value": "leak_check_mode"},
            ],
            value="analog_mode",
            clearable=False,
        )
    ],
    style=mode_style,
)

range_selection = html.Div(
    [
        dcc.Dropdown(
            id="range_selection",
            options=[
                {"label": "Range 1e-7", "value": 0},
                {"label": "Range 1e-8", "value": 1},
                {"label": "Range 1e-9", "value": 2},
                {"label": "Range 1e-10", "value": 3},
                {"label": "Range 1e-11", "value": 4},
                {"label": "Range 1e-12", "value": 5},
                {"label": "Range 1e-13", "value": 6},
            ],
            value=0,
            clearable=False,
        )
    ],
    style=mode_style,
)

accuracy_selection = html.Div(
    [
        dcc.Dropdown(
            id="accuracy_selection",
            options=[
                {"label": "Accuracy 0", "value": 0},
                {"label": "Accuracy 1", "value": 1},
                {"label": "Accuracy 2", "value": 2},
                {"label": "Accuracy 3", "value": 3},
                {"label": "Accuracy 4", "value": 4},
                {"label": "Accuracy 5", "value": 5},
            ],
            value=4,
            clearable=False,
        )
    ],
    style=mode_style,
)


start_mass = html.Div(
    [dcc.Input(id="start_mass", type="number", value=2, size="40pt")],
    style=massset_style1,
)

digital_mode_span: list[dict[str, str | int]] = [
    {"label": "Mass span: 10", "value": 0},
    {"label": "Mass span: 20", "value": 1},
    {"label": "Mass span: 50", "value": 2},
    {"label": "Mass span: 100", "value": 3},
    {"label": "Mass span: 150", "value": 4},
    {"label": "Mass span: 200", "value": 5},
    {"label": "Mass span: 300", "value": 6},
]

analog_mode_span: list[dict[str, str | int]] = [
    {"label": "Mass span: 4", "value": 0},
    {"label": "Mass span: 8", "value": 1},
    {"label": "Mass span: 32", "value": 2},
    {"label": "Mass span: 64", "value": 3},
]

leak_check_mode_span: list[dict[str, str | int]] = [
    {"label": "Mass span: None(This is leak check mode)", "value": 0}
]

mass_span = html.Div(
    [
        dcc.Dropdown(
            id="mass_span",
            options=analog_mode_span,
            value=0,
            clearable=False,
        )
    ],
    style=massset_style2,
)


basic_module = html.Div(
    [
        html.P("File name: ", style={"margin-left": "1%", "display": "inline-block"}),
        filename_input,
        filament_selection,
        html.P("Multiplier", style={"display": "inline-block"}),
        multiplier_onoff,
    ]
)
mode_module = html.Div([mode_selection, range_selection, accuracy_selection])
mass_setting_module = html.Div(
    [html.P("start mass: ", style={"display": "inline-block"}), start_mass, mass_span]
)
measurement_module = html.Div(
    [
        measure_button,
        dcc.Graph(id="Graph"),
        dcc.Interval(id="intervals", interval=1000, max_intervals=-1),
    ]
)  # << ここにグラフがはいる。
app.layout = html.Div(
    [
        html.H1("Q-mass spectroscopy", id="placeholder", style={"textAlign": "center"}),
        html.Hr(),
        basic_module,
        mode_module,
        mass_setting_module,
        html.Hr(),
        measurement_module,
        html.Hr(),
    ]
)

# callback


@app.callback(
    Output("mass_span", "options"),
    Input("range_selection", "value"),
    Input("accuracy_selection", "value"),
    Input("filament_selection", "value"),
    Input("multiplier", "on"),
    Input("mode_selection", "value"),
)
def set_condition(
    range: int,
    accuracy: int,
    filament: int,
    multiplier: bool,
    mode: str,
) -> list[dict[str, str | int]]:
    """[summary]

    Parameters
    ----------
    range : int
        [description]
    accuracy : int
        [description]
    multiplier : bool
        [description]
    mode : str
        [description]

    Returns
    -------
    list[dict[str, str|int]]
        [description]
    """

    if mode == "analog_mode":
        # q_mass.analog_mode()
        return analog_mode_span
    elif mode == "digital_mode":
        # q_mass.digital_mode()
        return digital_mode_span
    else:
        # q_mass.leak()
        return leak_check_mode_span


@app.callback(
    Output("intervals", "disabled"),
    Output("filename", "disabled"),
    Output("filament_selection", "disabled"),
    Output("multiplier", "disabled"),
    Output("mode_selection", "disabled"),
    Output("range_selection", "disabled"),
    Output("accuracy_selection", "disabled"),
    Output("start_mass", "disabled"),
    Output("mass_span", "disabled"),
    Input("measure_button", "on"),
)
def measure_starts(measure: bool) -> tuple[bool, ...]:
    if measure:
        return (False, True, True, True, True, True, True, True, True)
    else:
        return (True, False, False, False, False, False, False, False, False)


"""
@app.callback(
    Output("Graph", "figure"),
    Output("placeholder", "children")
    Input("intervals", "n_interval"),
    State("filename", "value"),
    State("mode_selection", "value"),
    State("range_selection", "value"),
    State("accuracy_selection", "value"),
    State("start_mass", "disabled"),
    State("mass_span", "value"),
)
def measureing(n: int, mass_span: int, range: int, accuracy: int):
    pass
"""

# main

if __name__ == "__main__":
    """Main routine"""
    """
    port = "/dev/ttyUSB0"
    q_mass = Qmass(
        port=port
        mode=0  ## Analog mode
        init = 2  ## Start mass
        p_range = 0  ## 1E-7 mbar
        accuracy =4
        span = 0
        output=""  ## file name. q_mass.f_save でアクセスできる。
    )
    q_mass.boot()
    """
    app.run_server(debug=True, host="0.0.0.0")
