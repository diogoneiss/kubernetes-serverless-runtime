import json
import logging
import os

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import redis
from dash import Input
from dash import Output
from dash import callback
from dash import dcc
from dash import html

UPDATE_TIME_IN_SECONDS = 10

dash.register_page(
    __name__,
    path="/",
    title="Home",
    name="Página principal",
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

def get_data_from_redis()-> tuple[dict, str]:
    logging.warn(f"Using [{REDIS_HOST}] as redis host.")
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
    METRICS_KEY = "diogoneiss-proj3-output"
    dict_data = r.get(METRICS_KEY)
    if not dict_data:
        print(f"No data found for key: {METRICS_KEY}")
        raise ValueError(f"No data found for key: {METRICS_KEY}")
    loaded_data =  json.loads(dict_data)
    timestamp_value = loaded_data.get("timestamp", "N/A")

    loaded_data.pop("timestamp", None)
    return loaded_data, timestamp_value

def create_figure(metrics: dict, title: str):
    x = []
    y = []
    for k, v in metrics.items():
        x.append(k)
        y.append(v)
    fig = px.bar(x=x, y=y, labels={"x": "Metric", "y": "Value"}, title=title)
    return fig

#TODO make layout a reference to a function that returns layout

# Defining the layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H1(
                    "Live Monitoring Dashboard", className="display-3 mb-3"
                ),
                html.P(
                    f"Monitoring information computed every {UPDATE_TIME_IN_SECONDS} seconds, displayed using live update ",
                    className="lead",
                ),
                html.Hr(className="my-2"),
                html.Div(
                    children=[
                        dcc.Loading(
                            id="loading-icon",
                            type="default",
                            overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                            children=dcc.Graph(id="metrics-bar-chart"),
                        ),
                        dcc.Interval(
                            id='interval-component',
                            interval=UPDATE_TIME_IN_SECONDS * 1000,  # Update every 5 seconds
                            n_intervals=0,
                            disabled=False
                        ),
                    ]),
            ],
            className="p-5 mb-4 bg-light rounded-3",
        ),
    ],
    style={"margin-top": "20px"},
)

@callback(
    Output('metrics-bar-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_bar_chart(n):
    data, timestamp_value = get_data_from_redis()
    title = f"Last updated: {timestamp_value}"
    fig = create_figure(data, title)
    return fig
