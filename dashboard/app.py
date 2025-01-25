import dash_bootstrap_components as dbc
from dash import Dash

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.ZEPHYR])
app.title = "Live monitoring"
server = app.server
