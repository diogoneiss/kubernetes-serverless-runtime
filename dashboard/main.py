import dash_bootstrap_components as dbc
from dash import html
from dash import page_container
from dash import page_registry

from app import app, server

special_style = {
    # "font-weight": "bold",
    "color": "white",
    # "background-color": "darkblue",
    # "padding": "10px",
    # "border-radius": "5px"
}

# Create the navigation items
paginas = []
for page in page_registry.values():
    paginas.append(
        dbc.NavItem(
            dbc.NavLink(
                page["name"], href=page["relative_path"], style=special_style
            )
        )
    )

# Create the navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Live Monitoring - Diogo Neiss", href="/"),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    paginas,
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
        fluid=True,
    ),
    color="primary",
    dark=True,
    className="mb-5",
)

# Define the app layout
app.layout = html.Div(
    [
        navbar,
        dbc.Container(
            [
                page_container,
            ],
            style={"margin-top": "20px"},
        ),
    ]
)


# Define the main function to run the app
def main() -> None:
    app.run_server(debug=False, host='0.0.0.0', port=9000)


# Run the app
if __name__ == "__main__":
    main()
