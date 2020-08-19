import pandas as pd


class Team_Metrics:
    def __init__(self, cycle_data, throughput, net_flow):
        self.cycle_data = cycle_data
        self.throughput = throughput
        self.net_flow = net_flow
        pd.options.plotting.backend = "plotly"

    def draw_throughput(self, throughput):
        fig = throughput.plot.line(x=throughput["Done"],y=throughput["Total"])
        fig.update_xaxes(
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        fig.update_layout(title='Productivity - How Much - "Do Lots"')
        return fig

    def draw_lead_time(self, cycle_data):
        fig = cycle_data.plot.line(
            x=cycle_data["Done"], y=cycle_data["Lead Time"])
        fig.update_layout(title='Responsivness - How Fast - "Do it Fast"')
        return fig

    def draw_defect_percentage(self, throughput):
        fig = throughput.plot(
            x=throughput["Done"],
            y=throughput["Defect Percentage"])
        fig.update_layout(title='Quality - How Well - "Do it Right"')
        return fig

    def draw_net_flow(self, cycle_data):
        fig = cycle_data.plot.bar(
            x=cycle_data["Done"],
            y=cycle_data["Net Flow"]
        )
        fig.update_layout(title=    'Predictability - How Repeatable - "Do it Predicably"')
        return fig

    def show_all(self):
        fig_throughput = self.draw_throughput(self.throughput)
        fig_defect_percentage = self.draw_defect_percentage(self.throughput)
        fig_lead_time = self.draw_lead_time(self.cycle_data)
        fig_net_flow = self.draw_net_flow(self.net_flow)

        fig_throughput.show()
        fig_defect_percentage.show()
        fig_lead_time.show()
        fig_net_flow.show()

    def show_dash(self):
        import dash
        import dash_core_components as dcc
        import dash_html_components as html

        fig_throughput = self.draw_throughput(self.throughput)
        fig_defect_percentage = self.draw_defect_percentage(self.throughput)
        fig_lead_time = self.draw_lead_time(self.cycle_data)
        fig_net_flow = self.draw_net_flow(self.net_flow)
        
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        app.layout = html.Div(children=[
            html.H1(children='Team Metrics'),

            html.Div(children=[
                dcc.Graph(id='throughput-graph', figure=fig_throughput),
                dcc.Graph(id='defect-percentage-graph', figure=fig_defect_percentage)],
                style={'columnCount': 2}),

            html.Div(children=[
                dcc.Graph(id='defect-lead_time-graph', figure=fig_lead_time),
                dcc.Graph(id='defect-net_flow', figure=fig_net_flow)
            ], style={'columnCount': 2})

        ])

        app.run_server(debug=False)