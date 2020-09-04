import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

class Dash:
    def __init__(self, team_metrics, config):
        super().__init__()
        self.config = config
        self.team_metrics = team_metrics

        self.app = dash.Dash(__name__)
        self.app.title = "Seshat - A Team Metrics app"

    def show_main_dash(self):
        tm = self.team_metrics
        fig_throughput = tm.draw_throughput("Total")
        fig_defect_percentage = tm.draw_defect_percentage("Total")
        fig_lead_time = tm.draw_lead_time("Total")
        fig_net_flow = tm.draw_net_flow("Total")

        app = self.app
        app.layout = html.Div(children=[
            html.H1(children='Team Metrics Main Dashoard'),

            html.Div([
                dcc.Dropdown(
                    id='issue-type-sel',
                    options=[{'label': i, 'value': i} for i in self.config["issue_type"]],
                    value='Total',
                    clearable=False
                    )], style={'width': '18%', 'left': 'right', 'display': 'inline-block'}),

            html.Div(children=[
                dcc.Graph(id='throughput-graph', figure=fig_throughput),
                dcc.Graph(id='defect-percentage-graph', figure=fig_defect_percentage),
                dcc.Graph(id='defect-lead_time-graph', figure=fig_lead_time),
                dcc.Graph(id='net_flow', figure=fig_net_flow)],
                style={'columnCount': 2}),
        ])

        app.callback(
            [Output('throughput-graph', 'figure'),
             Output('defect-percentage-graph', 'figure'),
             Output('defect-lead_time-graph', 'figure'),
             Output('net_flow', 'figure')],
            [Input('issue-type-sel', 'value')]
        )(self.update_main_dash)

    def show_hist_dash(self):
        tm = self.team_metrics
        fig_lead_time_hist = tm.draw_lead_time_hist("Total")

        figures = tm.draw_all_cycle_time_hist("Total")
        cycle_time_fig = []

        i = 0
        for fig in figures:
            i += 1
            cycle_time_fig.append(dcc.Graph(id="cycle-time-graph"+str(i),figure=fig))


        app = self.app
        app.layout = html.Div(children=[
            html.H1(children='Team Metrics Lead & Cicle Time'),

            html.Div([
                dcc.Dropdown(
                    id='issue-type-sel',
                    options=[{'label': i, 'value': i} for i in self.config["issue_type"]],
                    value='Total',
                    clearable=False
                    )], style={'width': '18%', 'left': 'right', 'display': 'inline-block'}),

            html.Div(children=[
                dcc.Graph(id='lead-time-graph', figure=fig_lead_time_hist),
                ],
                style={'columnCount': 1}),

            html.Div(id='cycle-time-graphs', children=cycle_time_fig, style={'columnCount': 3})
        ])

        app.callback(
            [Output('lead-time-graph', 'figure'),
            Output('cycle-time-graphs','children')],
            [Input('issue-type-sel', 'value')]
        )(self.update_hist_dash)

    def update_main_dash(self, type):
        tm = self.team_metrics
        fig_throughput = tm.draw_throughput(type)
        fig_defect_percentage = tm.draw_defect_percentage(type)
        fig_lead_time = tm.draw_lead_time(type)
        fig_net_flow = tm.draw_net_flow(type)
        return fig_throughput, fig_defect_percentage, fig_lead_time, fig_net_flow
    
    def update_hist_dash(self, type):
        tm = self.team_metrics
        fig_lead_time_hist = tm.draw_lead_time_hist(type)

        figures = tm.draw_all_cycle_time_hist(type)
        cycle_time_fig = []

        i = 0
        for fig in figures:
            i += 1
            cycle_time_fig.append(dcc.Graph(id="cycle-time-graph"+str(i),figure=fig))

        return fig_lead_time_hist, cycle_time_fig

    def run(self):
        self.app.run_server(debug=True)