#! /usr/bin/env python3
"""Dash を使ってDM2700の電圧をWebbrowserでみる"""

from __future__ import annotations

import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dmm2700
import plotly.express as px
from dash.dependencies import Input, Output

DATA_LENGTH: int = 200
voltages: list[float] = []
external_stylesheets: list[str] = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
reset = False

app.layout = html.Div(
    [
        html.H1(id="realtime-title", style={"textAlign": "center"}),
        daq.ToggleSwitch(id="Toggle_reset", value=False, label="RESET"),
        html.Div(id="toggle-switch-output"),
        dcc.Graph(id="dmm2700-output"),
        dcc.Interval(id="realtime-interval", interval=1000.0, max_intervals=-1),
        # interval 1000msは動作。100ms は難しい。数値だけなら800msでもOK
    ]
)


@app.callback(
    Output("toggle-switch-output", "children"), Input("Toggle_reset", "value")
)
def data_reset(value):
    global reset
    reset = value


@app.callback(  # Callback関数はInputインスタンスで指定した属性が更新されると
    # 呼び出され、その戻り値をOutputインスタンスで指定した属性に返す。
    Output("realtime-title", "children"),
    Output("dmm2700-output", "figure"),
    Input("realtime-interval", "n_intervals"),
)
def update_graphe(n_intervals):
    voltage = float(dm2700.measure())
    global voltages
    voltages.append(voltage)
    if len(voltages) > DATA_LENGTH:
        voltages.pop(0)
    if reset:
        voltages = []
    else:
        fig = px.line(x=range(len(voltages)), y=voltages)
    return (f"DMM2700 voltage chart: {voltage} / n_intervals: {n_intervals}", fig)


if __name__ == "__main__":
    dm2700 = dmm2700.DMM2700()
    dm2700.conf_voltage()
    app.run_server(debug=True, host="0.0.0.0")
