import pandas as pd
import plotly.graph_objects as go
import datetime
import statsmodels.api as sm
import numpy as np


class Team_Metrics:
    def __init__(self, cycle_data, throughput, net_flow):
        self.cycle_data = cycle_data
        self.throughput = throughput
        self.net_flow = net_flow
        pd.options.plotting.backend = "plotly"

    def draw_throughput(self, throughput):
        throughput = throughput.resample("W").sum()
        fig = throughput["Total"].plot.line(text=throughput["Total"])
        fig.update_layout(
            title='Productivity - How Much - "Do Lots"',
            showlegend=False,
            yaxis={'title': 'Throughput'}
            )

        fig = self.add_trendline(throughput, fig,"Total")     
        return fig

    def draw_lead_time(self, cycle_data):
        import calculator.flow
        lead_time = calculator.flow.avg_lead_time(cycle_data)
        fig = lead_time.plot.line()
        fig.update_layout(
            title='Responsivness - How Fast - "Do it Fast"',
            showlegend=False,
            yaxis={'title': 'Lead Time Avg'})
        fig = self.add_trendline(lead_time, fig,"Lead Time")     
        return fig

    def draw_defect_percentage(self, throughput):
        fig = throughput["Defect Percentage"].plot.line(text=throughput["Defect Percentage"])
        fig.update_layout(
            title='Quality - How Well - "Do it Right"',
            showlegend=False,
            yaxis={'title': 'Defect Percentage'})
        fig = self.add_trendline(throughput, fig, 'Defect Percentage')
        return fig

    def draw_net_flow(self, net_flow):
        net_flow["Color"] = np.where(net_flow["Net Flow"]<0,'red','blue') 
        fig = net_flow["Net Flow"].plot.bar(color=net_flow["Color"])
        fig.update_layout(
            title='Predictability - How Repeatable - "Do it Predictably"',
            showlegend=False,
            yaxis={'title': 'Net Flow'})
        fig = self.add_trendline(net_flow, fig, 'Net Flow')
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

    def add_trendline(self, df, fig, column):
        # This is needed because we can't use DateTimeIndex as input for OLS
        df['serialtime'] = [(d-datetime.datetime(1970,1,1)).days for d in df.index]
        df['bestfit'] = sm.OLS(df[column],sm.add_constant(df["serialtime"])).fit().fittedvalues
        fig = fig.add_trace(go.Scatter(
            x=df.index,
            y=df["bestfit"],
            mode='lines',
            line={'dash': 'dash'},
            marker_color="red"))
        return fig

    def add_range_buttons(self,fig):
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
        return fig

    def show_dash(self):
        import dash
        import dash_core_components as dcc
        import dash_html_components as html
        import dash_table

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
                dcc.Graph(id='defect-net_flow', figure=fig_net_flow)],
                style={'columnCount': 2}),

#            html.Div(children=[
#                 dash_table.DataTable(
#                    id='table',
#                    columns=[{"name": i, "id": i} for i in self.net_flow.columns],
#                    data=self.net_flow.to_dict('records'))])

        ])

        app.title = "Seshat - A Team Metrics app"
        app.run_server(debug=False)
