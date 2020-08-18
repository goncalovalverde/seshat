import pandas as pd

class Team_Metrics:
    def __init__(self, cycle_data, throughput, net_flow):
        self.cycle_data = cycle_data
        self.throughput = throughput
        self.net_flow = net_flow
        pd.options.plotting.backend = "plotly"

    def draw_throughput(self, throughput):
        fig = throughput["Total"].plot.line()
        return fig

    def draw_lead_time(self, cycle_data):
        fig = cycle_data.plot.scatter(
            x=cycle_data["Done"], y=cycle_data["Lead Time"])
        return fig

    def draw_defect_percentage(self, throughput):
        fig = throughput["Defect Percentage"].plot()
        return fig

    def draw_net_flow(self, cycle_data):
        fig = cycle_data["Net Flow"].plot.bar()
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

            html.Div(children='''How Much (Do lots).'''), ç 

            dcc.Graph(id='throughput-graph',figure=fig_throughput),

            html.Div(children='''How Well (Do lots).'''),

            dcc.Graph(id='defect-percentage-graph',figure=fig_defect_percentage)
           
        ])

        app.run_server(debug=True)