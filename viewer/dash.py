import dash
from dash_bootstrap_components._components.DropdownMenuItem import DropdownMenuItem
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import logging


class Dash:
    def __init__(self, projects, config):
        super().__init__()
        self.config = config
        self.team_metrics = projects[0]
        self.projects = projects
        external_stylesheets = [dbc.themes.SKETCHY]

        self.app = dash.Dash(
            __name__,
            external_stylesheets=external_stylesheets,
            suppress_callback_exceptions=True,
        )
        self.app.title = "Seshat - A Team Metrics app"
        self.server = self.app.server

        self.app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                self.navbar(),
                html.Div(id="page-content"),
            ]
        )

        self.app.callback(
            Output("page-content", "children"), [Input("url", "pathname")]
        )(self.display_page)

        self.app.callback(
            [
                Output("lead-time-graph", "figure"),
                Output("cycle-time-graphs", "children"),
            ],
            [Input("issue-type-sel-hist", "value")],
        )(self.update_hist_dash)

        self.app.callback(
            [
                Output("throughput-graph", "figure"),
                Output("defect-percentage-graph", "figure"),
                Output("lead_time-graph", "figure"),
                Output("net_flow", "figure"),
            ],
            [Input("issue-type-sel-main", "value")],
        )(self.update_main_dash)

        self.app.callback(
            [Output("wip-graph", "figure"), Output("start_stop-graph", "figure")],
            [Input("issue-type-sel-wip", "value")],
        )(self.update_wip_dash)

    def show_main_dash(self):
        logging.debug("Showing Main Team Metrics Dashboard")
        tm = self.team_metrics
        fig_throughput = tm.draw_throughput("Total")
        fig_defect_percentage = tm.draw_defect_percentage("Total")
        fig_lead_time = tm.draw_lead_time("Total")
        fig_net_flow = tm.draw_net_flow("Total")

        layout = html.Div(
            children=[
                html.H1(children="Team Metrics Main Dashboard"),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="issue-type-sel-main",
                            options=[{"label": i, "value": i} for i in tm.issue_types],
                            value="Total",
                            clearable=False,
                        )
                    ],
                    style={"width": "18%", "left": "right", "display": "inline-block"},
                ),
                html.Div(
                    children=[
                        dcc.Graph(id="throughput-graph", figure=fig_throughput),
                        dcc.Graph(
                            id="defect-percentage-graph", figure=fig_defect_percentage
                        ),
                        dcc.Graph(id="lead_time-graph", figure=fig_lead_time),
                        dcc.Graph(id="net_flow", figure=fig_net_flow),
                    ],
                    style={"columnCount": 2},
                ),
            ]
        )

        return layout

    def show_hist_dash(self):
        logging.debug("Showing Histogram Dashboard")
        tm = self.team_metrics
        fig_lead_time_hist = tm.draw_lead_time_hist("Total")

        figures = tm.draw_all_cycle_time_hist("Total")
        cycle_time_fig = []
        i = 0
        for fig in figures:
            i += 1
            cycle_time_fig.append(dcc.Graph(id="cycle-time-graph" + str(i), figure=fig))

        layout = html.Div(
            children=[
                html.H1(children="Team Metrics Lead & Cycle Time"),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="issue-type-sel-hist",
                            options=[{"label": i, "value": i} for i in tm.issue_types],
                            value="Total",
                            clearable=False,
                        )
                    ],
                    style={"width": "18%", "left": "right", "display": "inline-block"},
                ),
                html.Div(
                    children=[
                        dcc.Graph(id="lead-time-graph", figure=fig_lead_time_hist),
                    ],
                    style={"columnCount": 1},
                ),
                # TODO: [SES-33] Figure out how to improve the display of this graphics per columns
                html.Div(
                    id="cycle-time-graphs",
                    children=cycle_time_fig,
                    style={"columnCount": len(cycle_time_fig)},
                ),
            ]
        )

        return layout

    def show_raw_data(self):
        df = self.team_metrics.cycle_data
        layout = dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
        )
        return layout

    def show_wip_dash(self):
        tm = self.team_metrics
        fig_wip = tm.draw_wip("Total")
        fig_start_stop = tm.draw_start_stop("Total")

        layout = html.Div(
            children=[
                html.H1(children="Team Metrics WIP"),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="issue-type-sel-wip",
                            options=[{"label": i, "value": i} for i in tm.issue_types],
                            value="Total",
                            clearable=False,
                        )
                    ],
                    style={"width": "18%", "left": "right", "display": "inline-block"},
                ),
                html.Div(
                    children=[
                        dcc.Graph(id="wip-graph", figure=fig_wip),
                        dcc.Graph(id="start_stop-graph", figure=fig_start_stop),
                    ],
                    style={"columnCount": 1},
                ),
            ]
        )
        return layout

    def show_throughput_dash(self):
        tm = self.team_metrics
        fig_throughput = tm.draw_throughput("all")
        # TODO: improve this logic
        if tm.has_story_points:
            fig_velocity = tm.draw_velocity("Total")
            fig_spoints_throughput = tm.draw_story_points()
        else:
            fig_velocity = {}
            fig_spoints_throughput = {}

        layout = html.Div(
            children=[
                html.H1(children="Throughput"),
                html.Div(
                    children=[
                        dcc.Graph(id="throughput-graph", figure=fig_throughput),
                        dcc.Graph(id="velocity-graph", figure=fig_velocity),
                        dcc.Graph(
                            id="throughput-spoints-graph", figure=fig_spoints_throughput
                        ),
                    ],
                    style={"columnCount": 1},
                ),
            ]
        )
        return layout

    def update_main_dash(self, type):
        logging.debug("Updating main dashboard for type " + type)
        tm = self.team_metrics
        fig_throughput = tm.draw_throughput(type)
        fig_defect_percentage = tm.draw_defect_percentage(type)
        fig_lead_time = tm.draw_lead_time(type)
        fig_net_flow = tm.draw_net_flow(type)
        return fig_throughput, fig_defect_percentage, fig_lead_time, fig_net_flow

    def update_hist_dash(self, type):
        logging.debug("Updating Histograms to type " + type)
        tm = self.team_metrics
        fig_lead_time_hist = tm.draw_lead_time_hist(type)

        figures = tm.draw_all_cycle_time_hist(type)
        cycle_time_fig = []
        i = 0
        for fig in figures:
            i += 1
            cycle_time_fig.append(dcc.Graph(id="cycle-time-graph" + str(i), figure=fig))

        return fig_lead_time_hist, cycle_time_fig

    def update_wip_dash(self, type):
        logging.debug("Updating wip dashboard for type " + type)
        tm = self.team_metrics
        fig_wip = tm.draw_wip(type)
        fig_start_stop = tm.draw_start_stop(type)

        return fig_wip, fig_start_stop

    def navbar(self):
        dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Main Dashboard", href="/main_dashboard"),
                dbc.DropdownMenuItem("Lead & Cycle Time", href="/lead_cycle_time"),
                dbc.DropdownMenuItem("WIP", href="/wip"),
                dbc.DropdownMenuItem("Throughput", href="/throughput"),
                dbc.DropdownMenuItem("Raw Data", href="/raw_data"),
            ],
            nav=True,
            in_navbar=True,
            label="Explore",
        )

        project_menu = (
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem(project.name, href=f"/{str(i)}")
                    for i, project in enumerate(self.projects)
                ],
                nav=True,
                in_navbar=True,
                color="secondary",
                label="Select Project",
            )
            if len(self.projects) > 1
            else ""
        )

        navbar = dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(
                                        src=self.app.get_asset_url("metrics_icon.svg"),
                                        height="30px",
                                    )
                                ),
                                dbc.Col(
                                    dbc.NavbarBrand(
                                        "Seshat - Team Metrics Analysis",
                                        className="ml-2",
                                    )
                                ),
                            ],
                            align="center",
                            no_gutters=True,
                        ),
                        href="/home",
                    ),
                    dbc.NavbarToggler(id="navbar-toggler2"),
                    dbc.Collapse(
                        dbc.Nav(
                            [dropdown, project_menu], className="ml-auto", navbar=True
                        ),
                        id="navbar-collapse2",
                        navbar=True,
                    ),
                ]
            ),
            color="dark",
            dark=True,
            className="mb-4",
        )

        return navbar

    def display_page(self, pathname):
        if pathname:
            logging.debug("Changing page to " + pathname)
        if pathname == "/lead_cycle_time":
            return self.show_hist_dash()
        elif pathname == "/raw_data":
            return self.show_raw_data()
        elif pathname == "/wip":
            return self.show_wip_dash()
        elif pathname == "/throughput":
            return self.show_throughput_dash()
        else:
            import regex as re

            idx = re.search(r"\d+", pathname)
            if idx:
                self.team_metrics = self.projects[int(idx.group())]
            return self.show_main_dash()

    def run(self):
        self.app.run_server(debug=True)
