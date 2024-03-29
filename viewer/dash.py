import dash
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# from dash_extensions import Download
# from dash_extensions.snippets import send_data_frame
import logging
from flask.globals import request
import regex as re
from werkzeug.exceptions import BadRequestKeyError
import dash_pivottable

TOTAL = "Total"

class Dash:
    def __init__(self, projects, config: dict):
        super().__init__()
        self.config = config
        self.projects = projects
        self.debug = config["debug"]
        external_stylesheets = [dbc.themes.SKETCHY]

        self.app = dash.Dash(
            __name__,
            external_stylesheets=external_stylesheets,
            suppress_callback_exceptions=True,
            title="Seshat - A Team Metrics app",
        )
        self.server = self.app.server

        self.app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                self.navbar(),
                html.Div(id="page-content"),
            ]
        )

        self.app.callback(
            [Output("page-content", "children"), Output("nav-bar-brand", "children")],
            [Input("url", "pathname")],
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
            Output("download", "data"), [Input("download_csv_btn", "n_clicks")]
        )(self.export_to_csv)

        self.app.callback(
            [Output("wip-graph", "figure"), Output("start_stop-graph", "figure")],
            [Input("issue-type-sel-wip", "value")],
        )(self.update_wip_dash)

    def show_main_dash(self, team: int = 0):
        logging.debug("Showing Main Team Metrics Dashboard")
        tm = self.projects[team]
        fig_throughput = tm.draw_throughput(TOTAL)
        fig_defect_percentage = tm.draw_defect_percentage(TOTAL)
        fig_lead_time = tm.draw_lead_time(TOTAL)
        fig_net_flow = tm.draw_net_flow(TOTAL)

        layout = html.Div(
            children=[
                html.H1(children="Team Metrics Main Dashboard"),
                self.menu_pbi_types("main", team),
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

    def show_hist_dash(self, team: int = 0):
        logging.debug("Showing Histogram Dashboard")
        tm = self.projects[team]
        fig_lead_time_hist = tm.draw_lead_time_hist(TOTAL)

        figures = tm.draw_all_cycle_time_hist(TOTAL)
        cycle_time_fig = []
        i = 0
        for fig in figures:
            i += 1
            cycle_time_fig.append(dcc.Graph(id="cycle-time-graph" + str(i), figure=fig))

        layout = html.Div(
            children=[
                html.H1(children="Team Metrics Lead & Cycle Time"),
                self.menu_pbi_types("hist", team),
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

    def show_raw_data(self, team=0):
        tm = self.projects[team]
        df = tm.cycle_data

        layout = (
            html.Div(
                [
                    html.Button(
                        "Download data as CSV file", id="download_csv_btn", n_clicks=0
                    ),
                    dcc.Download(id="download"),
                ]
            ),
            dash_table.DataTable(
                id="table",
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict("records"),
            ),
        )
        return layout

    def show_wip_dash(self, team=0):
        tm = self.projects[team]
        fig_wip = tm.draw_wip(TOTAL)
        fig_start_stop = tm.draw_start_stop(TOTAL)

        layout = html.Div(
            children=[
                html.H1(children="Team Metrics Work In Progress (WIP)"),
                self.menu_pbi_types("wip", team),
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

    def show_throughput_dash(self, team=0):
        tm = self.projects[team]
        fig_throughput = tm.draw_throughput("all")
        # TODO: improve this logic
        if tm.has_story_points:
            fig_velocity = tm.draw_velocity(TOTAL)
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

    def show_cfd(self, team=0):
        logging.debug("Showing CFD")
        tm = self.projects[team]
        fig_cfd = tm.draw_cfd(TOTAL)

        layout = html.Div(
            children=[
                html.H1(children="CFD"),
                html.Div(children=[dcc.Graph(id="cfd-graph", figure=fig_cfd)]),
            ]
        )

        return layout

    def show_pivottable(self, team=0):
        tm = self.projects[team]
        cycle_names = [s for s in tm.workflow]

        # Create a new data frame to normalize data
        cycle_data = tm.cycle_data.copy()
        # Convert to date only (insted of date time)
        cycle_data[cycle_names] = (
            cycle_data[cycle_names].astype("<M8[D]").astype("<M8[ns]")
        )

        # Need to convert to list since this is what the
        data = cycle_data.values.tolist()
        data.insert(0, cycle_data.columns.to_list())
        layout = html.Div(
            children=[
                html.H1(children="Pivot Table"),
                html.Div(dash_pivottable.PivotTable(data=data)),
            ]
        )
        return layout

    def __get_team_index(self):
        try:
            return int(request.cookies["team_metrics_idx"])
        except BadRequestKeyError:
            return 0    

    def update_main_dash(self, pbi_type):
        team = self.__get_team_index()

        logging.debug("Updating main dashboard for PBI type %s", pbi_type)
        tm = self.projects[team]
        fig_throughput = tm.draw_throughput(pbi_type)
        fig_defect_percentage = tm.draw_defect_percentage(pbi_type)
        fig_lead_time = tm.draw_lead_time(pbi_type)
        fig_net_flow = tm.draw_net_flow(pbi_type)
        return fig_throughput, fig_defect_percentage, fig_lead_time, fig_net_flow

    def update_hist_dash(self, pbi_type):
        team = self.__get_team_index()

        logging.debug("Updating Histograms to PBI type %s", pbi_type)
        tm = self.projects[team]
        fig_lead_time_hist = tm.draw_lead_time_hist(pbi_type)

        figures = tm.draw_all_cycle_time_hist(pbi_type)
        cycle_time_fig = []
        i = 0
        for fig in figures:
            i += 1
            cycle_time_fig.append(dcc.Graph(id="cycle-time-graph" + str(i), figure=fig))

        return fig_lead_time_hist, cycle_time_fig

    def update_wip_dash(self, pbi_type):
        team = self.__get_team_index()

        logging.debug("Updating wip dashboard for PBI type %s", pbi_type)
        tm = self.projects[team]
        fig_wip = tm.draw_wip(pbi_type)
        fig_start_stop = tm.draw_start_stop(pbi_type)

        return fig_wip, fig_start_stop

    def navbar(self):
        dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Main Dashboard", href="/main_dashboard"),
                dbc.DropdownMenuItem("Lead & Cycle Time", href="/lead_cycle_time"),
                dbc.DropdownMenuItem("WIP", href="/wip"),
                dbc.DropdownMenuItem("Throughput", href="/throughput"),
                dbc.DropdownMenuItem("CFD", href="/cfd"),
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
                                        self.app.title,
                                        className="ml-2",
                                        id="nav-bar-brand",
                                    )
                                ),
                            ],
                            align="center",
                            className="g-0",
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

    def menu_pbi_types(self, dashboard, team):
        tm = self.projects[team]
        menu_pbi_types = (
            html.Div(
                [
                    dcc.Dropdown(
                        id=f"issue-type-sel-{dashboard}",
                        options=[{"label": i, "value": i} for i in tm.pbi_types],
                        value=TOTAL,
                        clearable=False,
                    )
                ],
                style={"width": "18%", "left": "right", "display": "inline-block"},
            )
            if len(tm.pbi_types) > 2
            else ""
        )

        return menu_pbi_types

    def export_to_csv(self, n_clicks):
        team = self.__get_team_index()

        tm = self.projects[team]

        if n_clicks > 0:
            logging.debug("Downloading CSV file")
            return dcc.send_data_frame(
                tm.cycle_data.to_csv,
                filename=f"{tm.name}.csv",
            )

    def display_page(self, pathname):

        idx = re.search(r"/(\d+)", pathname)
        if idx:
            team = int(idx.group(1))
            dash.callback_context.response.set_cookie("team_metrics_idx", str(team))
        else:
            self.__get_team_index()

        title = f"{self.app.title} : {self.projects[team].name}"

        if pathname:
            logging.debug("Changing page to %s", pathname)
        if pathname == "/lead_cycle_time":
            return self.show_hist_dash(team), title
        if pathname == "/raw_data":
            return self.show_raw_data(team), title
        if pathname == "/wip":
            return self.show_wip_dash(team), title
        if pathname == "/throughput":
            return self.show_throughput_dash(team), title
        if pathname == "/cfd":
            return self.show_cfd(team), title
        if pathname == "/pivot":
            return self.show_pivottable(team), title

        return self.show_main_dash(team), title

    def run(self):
        self.app.run_server(debug=self.debug)
