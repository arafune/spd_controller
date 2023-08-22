"""Dash tuning mirror layout."""

from typing import Literal

import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html

NLORDER = Literal[1, 3]


def mirror_move_button(nl_order: NLORDER) -> dbc.ButtonGroup:
    """Mirror move button."""
    return dbc.ButtonGroup(
        [
            dbc.Button("▲", color="primary", id=f"up_{nl_order}"),
            dbc.ButtonGroup(
                [
                    dbc.Button(
                        "◀",
                        color="primary",
                        id=f"left_{nl_order}",
                    ),
                    dbc.Button(
                        "■",
                        color="primary",
                        id=f"stop_{nl_order}",
                    ),
                    dbc.Button(
                        "▶",
                        color="primary",
                        id=f"right_{nl_order}",
                    ),
                    dbc.Tooltip(
                        "Clockwise rotation indefinitely (move down)",
                        target=f"down_{nl_order}",
                        placement="top",
                    ),
                    dbc.Tooltip(
                        "AntiClockwise rotation indefinitely (move top)",
                        target=f"up_{nl_order}",
                        placement="top",
                    ),
                    dbc.Tooltip(
                        "Clockwise rotation indefinitely",
                        target=f"right_{nl_order}",
                        placement="top",
                    ),
                    dbc.Tooltip(
                        "Anti-Clockwise rotation indefinitely",
                        target=f"left_{nl_order}",
                        placement="top",
                    ),
                    dbc.Tooltip(
                        "Stop rotation",
                        target=f"stop_{nl_order}",
                        placement="top",
                    ),
                ],
            ),
            dbc.Button("▼", color="primary", id=f"down_{nl_order}"),
        ],
        vertical=True,
        style={"marginTop": "1em", "marginLeft": "1em"},
    )


def position_display(nl_order: NLORDER) -> list:
    """Position display.

    [TODO:description]

    Parameters
    ----------
    nl_order: NLORDER
        1 or 3

    Returns
    -------
    list
        [TODO:description]
    """
    return [
        daq.LEDDisplay(
            value="0",
            color="red",
            id=f"position_h_{nl_order}ω",
            size=24,
            style={"marginLeft": "1em", "display": "inline-block"},
        ),
        html.P(
            "/",
            style={"display": "inline-block", "marginLeft": "1em", "font-size": "250%"},
        ),
        daq.LEDDisplay(
            value="0",
            color="red",
            id=f"position_v_{nl_order}ω",
            size=24,
            style={"marginLeft": "3em", "display": "inline-block"},
        ),
    ]


def speed_change_button(nl_order: NLORDER) -> html.Div:
    """Provide speed change selection button.

    [TODO:description]

    Parameters
    ----------
    nl_order
        [TODO:description]

    Returns
    -------
    html.Div
        [TODO:description]
    """
    return html.Div(
        [
            html.P(
                children="Max",
                id=f"current_velocity_{nl_order}",
                style={"display": "inline_block", "marginLeft": "2em"},
            ),
            dbc.DropdownMenu(
                label="velocity",
                id=f"velocity_{nl_order}",
                children=[
                    dbc.DropdownMenuItem(
                        "Max",
                        id=f"velocity_{nl_order}_max",
                    ),
                    dbc.DropdownMenuItem(
                        "Middle",
                        id=f"velocity_{nl_order}_middle",
                    ),
                    dbc.DropdownMenuItem(
                        "Slow",
                        id=f"velocity_{nl_order}_min",
                    ),
                ],
                style={"display": "inline-block", "marginLeft": "2em"},
            ),
            dbc.Tooltip(
                "Max: 2000, Middle 200, Low:20",
                target=f"velocity_{nl_order}",
                placement="top",
            ),
        ],
        style={"display": "inline-block", "marginLeft": "2em"},
    )


def move_by_step(nl_order: NLORDER) -> html.Div:
    """Provide 'move by step' component.

    [TODO:description]

    Parameters
    ----------
    nl_order: NLORDER
        1 or 3

    Returns
    -------
    html.Div
        [TODO:description]
    """
    return html.Div(
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
                id=f"movement_{nl_order}",
                style={
                    "display": "inline-block",
                    "width": "10em",
                    "marginLeft": "2em",
                },
            ),
            dbc.Button(
                "H",
                color="primary",
                id=f"move_h_{nl_order}",
                style={
                    "display": "inline-block",
                    "marginLeft": "1em",
                    "marginBottom": "0.3em",
                },
            ),
            dbc.Button(
                "V",
                color="primary",
                id=f"move_v_{nl_order}",
                style={
                    "display": "inline-block",
                    "marginLeft": "1em",
                    "marginBottom": "0.3em",
                },
            ),
        ],
        style={
            "display": "flex",
            "justify-content": "center",
            "marginLeft": "1em",
            "marginTop": "0.5em",
            "marginBottom": "0.3em",
        },
    )


def mirror_component(nl_order: NLORDER) -> html.Div:
    """Provide Mirror control component.

    Parameters
    ----------
    nl_order: NLORDER
        non linear order (1 or 3)
    """
    return html.Div(
        [
            html.H3(
                f"Mirror {nl_order}ω",
                style={
                    "text-align": "center",
                    "marginTop": "0.5em",
                    "marginBottom": "0.5em",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [*position_display(nl_order)],
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            "marginLeft": "1em",
                            "marginTop": "0.5em",
                            "marginBottom": "0.3em",
                        },
                    ),
                    html.Div(
                        [
                            mirror_move_button(nl_order),
                            speed_change_button(nl_order),
                        ],
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            "marginTop": "1.5em",
                        },
                    ),
                    move_by_step(nl_order),
                ],
            ),
        ],
        id=f"mirror_{nl_order}",
        style={
            "width": "40%",
            "border-style": "solid",
            "border-radius": "10pt",
            "border-color": "red",
            "marginLeft": "5%",
            "marginRight": "5%",
            "marginTop": "2%",
            "marginBottom": "5%",
            "display": "inline-block",
        },
    )


flipper1_button = dbc.Button(
    "Flipper1",
    color="danger",
    id="flipper_1",
    style={
        "display": "inline-block",
        "marginLeft": "1em",
        "marginBottom": "0.3em",
    },
)


flipper2_button = dbc.Button(
    "Flipper1",
    color="danger",
    id="flipper_1",
    style={
        "display": "inline-block",
        "marginLeft": "1em",
        "marginBottom": "0.3em",
    },
)
