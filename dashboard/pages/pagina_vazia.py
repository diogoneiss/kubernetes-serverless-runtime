import os

import dash
from dash import html

dash.register_page(
    __name__,
    path="/about",
    title="Sobre",
    name="Sobre",
)

layout = html.Div(
    [
        html.H2(
            "Sobre",
            style={"textAlign": "center"},
        ),
        html.P(
            "Projeto de cloud computing sobre monitoramento de aplicações.",
            style={"textAlign": "start", "margin-bottom": "30px", "margin-top": "30px"},
        )
    ]
)
