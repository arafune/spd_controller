#! /usr/bin/env python3
"""Lakeshore temperature monitor
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Literal
from unittest.mock import MagicMock

import dash
import dash_daq as daq
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html

try:
    import pyvisa
except ModuleNotFoundError:
    from random import random
    from unittest.mock import MagicMock

channel_type = Literal["A", "B"]


def read_temperature(channel: channel_type = "A") -> float:
    inst.write("SCHN {}".format(channel))
    inst.write("SDAT?")
    return float(inst.read())


date_axis: list[datetime.datetime] = []
temperatures: list[float] = []

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Lakeshore330",
    update_title=None,
    suppress_callback_exceptions=True,
)

filename_input_style = {
    "width": "70%",
    "display": "inline-block",
    "verticalAlign": "center",
    "margin-left": "10%",
}

save_sw_style = {
    "display": "inline-block",
    "verticalAlign": "center",
    "margin-left": 15,
}

file_name_input = dcc.Input(
    id="filename",
    type="text",
    debounce=True,
    placeholder="File name",
    persistence=True,
    persistence_type="local",
    style=filename_input_style,
)

save_sw = daq.BooleanSwitch(
    id="save_sw",
    on=False,
    label="Save",
    labelPosition="top",
    disabled=True,
    persistence=True,
    persistence_type="local",
    style=save_sw_style,
)

current_T = daq.LEDDisplay(
    id="current_temp_display",
    label="Temperature",
    value="  1.23",
    size=188,
    color="red",
    style={"display": "inline-block", "vertical-align": "middle", "width": "800px"},
)


show_all_region_button = html.Button(
    "Show_all_range",
    id="show_all",
    n_clicks=0,
)

dl_data_button = html.Button("Download", id="dwn_ld_button", n_clicks=0)

all_data_buttons = html.Div(
    [
        show_all_region_button,
        html.P(),
        dl_data_button,
        dcc.Download(id="download_data"),
    ],
    style={"display": "inline-block", "vertical-align": "middle"},
)

first_row = html.Div([file_name_input, save_sw], style={"margin": "auto"})
second_row = html.Div(
    [
        current_T,
        dcc.Graph(
            id="temperature_graph",
            style={"display": "inline-block", "vertical-align": "middle"},
        ),
    ],
    style={"margin": "auto"},
)

third_row = html.Div(
    [
        all_data_buttons,
        dcc.Graph(
            id="all_range_graph",
            style={
                "display": "inline-block",
                "width": "1200px",
                "vertical-align": "middle",
            },
        ),
    ]
)

app.layout = html.Div(
    [
        html.H1("Lakeshore 330", style={"textAlign": "center"}),
        first_row,
        second_row,
        dcc.Interval(id="realtime_interval", interval=1000),
        html.Div(id="all_region", children=[]),
    ],
    id="base_layout",
)


@app.callback(
    Output("save_sw", "disabled"),
    Output("save_sw", "on"),
    State("save_sw", "on"),
    Input("filename", "value"),
)
def enable_save_sw(sw_onoff, filename):
    try:
        if filename:
            return False, sw_onoff
        else:
            return True, False
    except NameError:
        return True, False


@app.callback(Output("all_region", "children"), Input("save_sw", "on"))
def show_all_region_graph(sw_onoff):
    if sw_onoff:
        return third_row


max_data_length: int = 300


@app.callback(
    Output("download_data", "data"),
    State("filename", "value"),
    Input("dwn_ld_button", "n_clicks"),
)
def dl_data(filename: str, n_clicks: int):
    if n_clicks > 0:
        return dcc.send_file(filename)


#
@app.callback(
    Output("all_range_graph", "figure"),
    State("filename", "value"),
    Input("show_all", "n_clicks"),
)
def plot_all(filename, n_clicks: int):
    if n_clicks > 0:
        fp = tempfile.NamedTemporaryFile()
        shutil.copy(filename, fp.name)
        all_region_data = load_log(fp.name)
        return {"data": [go.Scatter(x=all_region_data[0], y=all_region_data[1])]}
    else:
        return {"data": [go.Scatter(x=[0], y=[0])]}


@app.callback(
    Output("current_temp_display", "value"),
    Output("temperature_graph", "figure"),
    State("save_sw", "on"),
    State("filename", "value"),
    Input("realtime_interval", "n_intervals"),
)
def update_temperature(
    save_sw: bool, log_filename: str, n_interval: int
) -> tuple(str, dict[str, list[FigureWidget]]):
    temperature = read_temperature("A")
    now = datetime.now()
    date_axis.append(now)
    temperatures.append(temperature)
    if len(date_axis) > max_data_length:
        date_axis.pop(0)
        temperatures.pop(0)
    if save_sw:
        with open(log_filename, mode="a") as store_file:
            store_file.write(
                "{}\t{}\n".format(now.strftime("%Y/%m/%d %H:%M:%S"), temperature)
            )
    return (
        "{:.2f}".format(temperature),
        {"data": [go.Scatter(x=date_axis, y=temperatures)]},
    )


def load_log(filename: str | Path) -> tuple[list[datetime], list[float]]:
    date_time: list[datetime] = []
    temperatures: list[float] = []
    with open(filename, mode="r") as f:
        for line in f:
            tmp = line.split("\t")
            date_time.append(datetime.strptime(tmp.pop(0), "%Y/%m/%d %H:%M:%S"))
            temperatures.append(float(tmp.pop()))
    return date_time, temperatures


if __name__ == "__main__":
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource("GPIB::12")
        inst.write("*IDN?")
        if "LSCI,MODEL330" in inst.read():
            inst.write("CCHN A")
            inst.write("CUNI K")
            inst.write("SUNI K")
            inst.write("*OPC")
            inst.write("CCHN B")
            inst.write("CUNI K")
            inst.write("SUNI K")
            inst.write("*OPC")
    except NameError:
        inst = MagicMock
        # side_effect = [random() for _ in range(50)]
        inst.read = MagicMock(side_effect=random)
        inst.write = MagicMock(return_value=None)

    app.run_server(debug=True, host="0.0.0.0")
