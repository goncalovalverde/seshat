import pandas as pd
import plotly.graph_objects as go
import datetime
import statsmodels.api as sm
import numpy as np
import calculator.flow


class Team_Metrics:
    def __init__(self, cycle_data, throughput, config):
        self.cycle_data = cycle_data
        self.throughput = throughput
        self.config = config
        pd.options.plotting.backend = "plotly"


    def draw_throughput(self, throughput, type):
        throughput = throughput.resample("W").sum()
        fig = throughput[type].plot.line(text=throughput[type])
        fig.update_layout(
            title='Productivity - How Much - "Do Lots"',
            showlegend=False,
            yaxis={'title': 'Throughput'}
            )

        fig = self.add_trendline(throughput, fig, type)
        return fig

    def draw_lead_time(self, cycle_data, type):
        lead_time = calculator.flow.avg_lead_time(cycle_data, type)
        fig = lead_time.plot.line()
        fig.update_layout(
            title='Responsivness - How Fast - "Do it Fast"',
            showlegend=False,
            yaxis={'title': 'Lead Time Avg'})
        fig = self.add_trendline(lead_time, fig, "Lead Time")
        return fig

    def draw_defect_percentage(self, throughput, type):
        throughput = calculator.flow.defect_percentage(throughput, type)
        fig = throughput["Defect Percentage"].plot.line(text=throughput["Defect Percentage"])
        fig.update_layout(
            title='Quality - How Well - "Do it Right"',
            showlegend=False,
            yaxis={'title': 'Defect Percentage'})
        fig = self.add_trendline(throughput, fig, 'Defect Percentage')
        return fig

    def draw_net_flow(self, cycle_data, type):
        net_flow = calculator.flow.net_flow(cycle_data, type)
        net_flow["Color"] = np.where(net_flow["Net Flow"] < 0, 'red', 'blue')
        fig = net_flow["Net Flow"].plot.bar(color=net_flow["Color"])
        fig.update_layout(
            title='Predictability - How Repeatable - "Do it Predictably"',
            showlegend=False,
            yaxis={'title': 'Net Flow'})
        fig = self.add_trendline(net_flow, fig, 'Net Flow')
        return fig

    def draw_lead_time_hist(self, cycle_data, type):
        fig = cycle_data["Lead Time"].plot.hist()
        return fig

    def show_all(self):
        fig_throughput = self.draw_throughput(self.throughput, "Total")
        fig_defect_percentage = self.draw_defect_percentage(self.throughput)
        fig_lead_time = self.draw_lead_time(self.cycle_data)
        fig_net_flow = self.draw_net_flow(self.cycle_data)

        fig_throughput.show()
        fig_defect_percentage.show()
        fig_lead_time.show()
        fig_net_flow.show()

    def add_trendline(self, df, fig, column):
        # This is needed because we can't use DateTimeIndex as input for OLS
        df['serialtime'] = [(d-datetime.datetime(1970, 1, 1)).days for d in df.index]
        df['bestfit'] = sm.OLS(df[column], sm.add_constant(df["serialtime"])).fit().fittedvalues
        fig = fig.add_trace(go.Scatter(
            x=df.index,
            y=df["bestfit"],
            mode='lines',
            line={'dash': 'dash'},
            marker_color="red"))
        return fig

    def add_range_buttons(self, fig):
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

    # TODO: [SES-20] Migrate to a separate file (need to refactor the dashboard part)

