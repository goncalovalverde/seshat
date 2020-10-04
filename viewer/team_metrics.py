import pandas as pd
import plotly.graph_objects as go
import datetime
import statsmodels.api as sm
import numpy as np
import calculator.flow


# TODO: refactor to remove cycle_data and throughput to invocation of internal
# methods and use the class properties instead
class Team_Metrics:
    def __init__(self, cycle_data, throughput, config):
        self.cycle_data = cycle_data
        self.throughput = throughput
        self.config = config
        pd.options.plotting.backend = "plotly"

    def draw_throughput(self, type):
        throughput = self.throughput
        throughput = throughput.resample("W").sum()
        fig = throughput[type].plot.line(text=throughput[type])
        fig.update_layout(
            title='Productivity - How Much - "Do Lots"',
            showlegend=False,
            yaxis={'title': 'Throughput'}
            )

        fig = self.add_trendline(throughput, fig, type)
        return fig

    def draw_lead_time(self, type):
        lead_time = calculator.flow.avg_lead_time(self.cycle_data, type)
        fig = lead_time.plot.line()
        fig.update_layout(
            title='Responsiveness - How Fast - "Do it Fast"',
            showlegend=False,
            yaxis={'title': 'Lead Time Avg'})
        fig = self.add_trendline(lead_time, fig, "Lead Time")
        return fig

    def draw_defect_percentage(self, type):
        throughput = self.throughput
        throughput = calculator.flow.defect_percentage(throughput, type)
        fig = throughput["Defect Percentage"].plot.line(
            text=throughput["Defect Percentage"])
        fig.update_layout(
            title='Quality - How Well - "Do it Right"',
            showlegend=False,
            yaxis={'title': 'Defect Percentage'})
        fig = self.add_trendline(throughput, fig, 'Defect Percentage')
        return fig

    def draw_net_flow(self, type):
        net_flow = calculator.flow.net_flow(self.cycle_data, type)
        net_flow = net_flow.resample("W").sum()
        net_flow["Color"] = np.where(net_flow["Net Flow"] < 0, 'red', 'blue')
        fig = net_flow["Net Flow"].plot.bar(color=net_flow["Color"])
        fig.update_layout(
            title='Predictability - How Repeatable - "Do it Predictably"',
            showlegend=False,
            yaxis={'title': 'Net Flow'})
        fig = self.add_trendline(net_flow, fig, 'Net Flow')
        return fig

    def draw_wip(self, type):
        wip = calculator.flow.net_flow(self.cycle_data, type)
        wip = wip.resample("W").sum()
        fig = wip["WIP"].plot.bar()
        fig.update_layout(
            title="Work in Progress",
            showlegend=False,
            xaxis={'title': 'Week'},
            yaxis={'title': 'WIP'}
        )
        return fig

    def draw_start_stop(self, type):
        start = calculator.flow.group_by_date(self.cycle_data, "Created")
        start = start.resample("W").sum()
        end = calculator.flow.group_by_date(self.cycle_data, "Done")
        end = end.resample("W").sum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=start.index,
            y=start[type],
            mode='lines',
            name='Created')
        )
        fig.add_trace(go.Scatter(
            x=end.index,
            y=end[type],
            mode='lines',
            name='Done'
        ))

        fig.update_layout(
            legend_xanchor="left",
            legend_x=0.01,
            title='Created vs Done'
        )
        return fig

    def draw_lead_time_hist(self, type):
        lead_time = self.cycle_data[["Done", "Type", "Lead Time"]].copy()
        if type != "Total":
            lead_time = lead_time.loc[lead_time["Type"] == type]

        fig = lead_time["Lead Time"].plot.hist()
        fig.update_traces(xbins_size=1)
        fig.update_layout(
            title='Lead Time ' + type,
            showlegend=False,
            yaxis={'title': 'Lead time'},
            xaxis={'title': 'days'},
            )

        fig = self.add_percentile(lead_time["Lead Time"], fig)
        return fig

    def draw_cycle_time_hist(self, type, wkflow_step):
        cycle_data = self.cycle_data
        cycle_time_name = "Cycle Time " + wkflow_step
        cycle_time = cycle_data[["Done", "Type", cycle_time_name]].copy()
        if type != "Total":
            cycle_time = cycle_time.loc[cycle_time["Type"] == type]

        cycle_time = cycle_time.loc[cycle_time[cycle_time_name] > 0]

        fig = cycle_time[cycle_time_name].plot.hist()
        fig.update_traces(xbins_size=1)
        fig.update_layout(
            title=cycle_time_name,
            showlegend=False,
            yaxis={'title': 'Cycle time'},
            xaxis={'title': 'days'}
            )
        
        fig = self.add_percentile(cycle_time[cycle_time_name], fig)
        return fig

    def draw_all_cycle_time_hist(self, type):
        workflow_keys = list(self.config["Workflow"].keys())
        figures = []

        for i in range(len(workflow_keys)-1):
            wkflow_step = workflow_keys[i]
            fig = self.draw_cycle_time_hist(type, wkflow_step)
            figures.append(fig)

        return figures

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
        df['bestfit'] = sm.OLS(
            df[column], 
            sm.add_constant(df["serialtime"])
            ).fit().fittedvalues
        fig = fig.add_trace(go.Scatter(
            x=df.index,
            y=df["bestfit"],
            mode='lines',
            line={'dash': 'dash'},
            marker_color="red"))
        return fig
    
    def add_percentile(self, df, fig):
        percentile = df.quantile([.5, .85, .95])


        fig = fig.add_shape(
            type="line",
            yref="paper",
            x0=percentile[.85],
            y0=0,
            x1=percentile[.85],
            y1=.95,
            line_dash="dash"
        )

        fig = fig.add_annotation(
            x=percentile[.85]+5,
            yref="paper",
            y=.85,
            showarrow=False,
            text="85%"
        )
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
