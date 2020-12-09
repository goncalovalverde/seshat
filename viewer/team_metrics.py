import pandas as pd
import plotly.graph_objects as go
import numpy as np
import calculator.flow
import logging
import viewer.tools


# TODO: refactor to remove cycle_data and throughput to invocation of internal
# methods and use the class properties instead
class Team_Metrics:
    def __init__(self, cycle_data, config):
        self.cycle_data = cycle_data
        self.throughput = calculator.flow.throughput(self.cycle_data)

        self.workflow = config["Workflow"]

        # Extract the beggining and end of the workflow
        self.start_column = list(self.workflow.keys())[0]
        self.end_column = list(self.workflow.keys())[-1]

        self.name = config["name"]
        self.has_story_points = True if "Story Points" in cycle_data else False

        self.issue_types = cycle_data["Type"].unique().tolist()
        # Append pseudo issue type "Total"
        self.issue_types.insert(0, "Total")

        pd.options.plotting.backend = "plotly"

    def draw_throughput(self, type):
        logging.debug("Showing throughput graph for " + type)
        throughput = self.throughput
        throughput = throughput.resample("W").sum()

        if type == "all":
            fig = throughput.plot.line(
                title="Throughput : how many PBI's delivered",
                labels={"value": "Throughput", "variable": "Issue Type"},
            )
        else:
            fig = throughput[type].plot.line(
                labels={"value": "Throughput"}, text=throughput[type]
            )

        fig.update_traces(textposition="top center")

        if type != "all":
            fig.update_layout(
                title='Productivity - How Much - "Do Lots"', showlegend=False
            )

            fig = viewer.tools.add_trendline(throughput, fig, type)

        return fig

    def add_velocity(self, fig):
        velocity = calculator.flow.velocity(self.cycle_data).resample("W").sum()
        fig = fig.add_trace(
            go.Scatter(
                x=velocity.index,
                y=velocity["Total"],
                name="Velocity",
                mode="lines",
                line={"dash": "dash"},
                marker_color="red",
            )
        )
        return fig

    def draw_velocity(self, type):
        velocity = calculator.flow.velocity(self.cycle_data).resample("W").sum()
        fig = velocity[type].plot.line()

        fig.update_layout(
            title="Velocity : How much story points delivered?",
            yaxis={"title": "Story Points"},
        )

        fig = viewer.tools.add_trendline(velocity, fig, "Total")
        return fig

    def draw_story_points(self):
        try:
            story_points = (
                calculator.flow.story_points(self.cycle_data).resample("W").sum()
            )
            fig = story_points.plot.line(
                title="Velocity: Distribution of story points delivered",
                labels={"value": "Count of Story Points"},
            )

            return fig
        except AttributeError:
            logging.error(
                "No valid Story Points found. Are you sure you configured the custom field right?"
            )
            return {}

    def draw_lead_time(self, type):
        lead_time = calculator.flow.avg_lead_time(self.cycle_data, type)
        fig = lead_time.plot.line()
        fig.update_layout(
            title='Responsiveness - How Fast - "Do it Fast"',
            showlegend=False,
            yaxis={"title": "Lead Time Avg"},
        )
        fig = viewer.tools.add_trendline(lead_time, fig, "Lead Time")
        return fig

    def draw_defect_percentage(self, type):
        throughput = self.throughput
        throughput = calculator.flow.defect_percentage(throughput, type)
        fig = throughput["Defect Percentage"].plot.line(
            text=throughput["Defect Percentage"]
        )
        fig.update_traces(texttemplate="%{text:%}", textposition="top center")
        fig.update_layout(
            title='Quality - How Well - "Do it Right"',
            showlegend=False,
            yaxis={"title": "Defect Percentage", "tickformat": ".0%"},
        )
        fig = viewer.tools.add_trendline(throughput, fig, "Defect Percentage")
        return fig

    def draw_net_flow(self, type):
        logging.debug("Drawing Net Flow")

        net_flow = calculator.flow.net_flow(
            self.cycle_data, self.start_column, self.end_column, type
        )
        net_flow = net_flow.resample("W").sum()
        net_flow["Color"] = np.where(net_flow["Net Flow"] < 0, "red", "blue")
        fig = net_flow["Net Flow"].plot.bar(color=net_flow["Color"])
        fig.update_layout(
            title='Predictability - How Repeatable - "Do it Predictably"',
            showlegend=False,
            yaxis={"title": "Net Flow"},
        )
        fig = viewer.tools.add_trendline(net_flow, fig, "Net Flow")
        return fig

    def draw_wip(self, type):
        wip = calculator.flow.net_flow(
            self.cycle_data, self.start_column, self.end_column, type
        )
        fig = wip["WIP"].plot.bar()
        fig.update_layout(
            title="Work in Progress",
            showlegend=False,
            xaxis={"title": "Week"},
            yaxis={"title": "WIP"},
        )
        return fig

    def draw_start_stop(self, type):
        start = calculator.flow.group_by_date(self.cycle_data, self.start_column)
        start = start.resample("W").sum()
        end = calculator.flow.group_by_date(self.cycle_data, self.end_column)
        end = end.resample("W").sum()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=start.index, y=start[type], mode="lines", name=self.start_column
            )
        )
        fig.add_trace(
            go.Scatter(x=end.index, y=end[type], mode="lines", name=self.end_column)
        )

        fig.update_layout(legend_xanchor="left", legend_x=0.01, title="Started vs Done")
        return fig

    def draw_lead_time_hist(self, type):
        lead_time = self.cycle_data[[self.end_column, "Type", "Lead Time"]].copy()
        if type != "Total":
            lead_time = lead_time.loc[lead_time["Type"] == type]

        fig = lead_time["Lead Time"].plot.hist()
        fig.update_traces(xbins_size=1)
        fig.update_layout(
            title="Lead Time " + type,
            showlegend=False,
            yaxis={"title": "Lead time"},
            xaxis={"title": "days"},
        )

        fig = viewer.tools.add_percentile(lead_time["Lead Time"], fig)
        return fig

    def draw_cycle_time_hist(self, type, wkflow_step):
        cycle_data = self.cycle_data
        cycle_time_name = "Cycle Time " + wkflow_step
        logging.debug(f"Showing histogram for {cycle_time_name}")

        try:
            cycle_time = cycle_data[[self.end_column, "Type", cycle_time_name]].copy()
            if type != "Total":
                cycle_time = cycle_time.loc[cycle_time["Type"] == type]

            cycle_time = cycle_time.loc[cycle_time[cycle_time_name] > 0]

            fig = cycle_time[cycle_time_name].plot.hist()
            fig.update_traces(xbins_size=1)
            fig.update_layout(
                title=cycle_time_name,
                showlegend=False,
                yaxis={"title": "Cycle time"},
                xaxis={"title": "days"},
            )

            fig = viewer.tools.add_percentile(cycle_time[cycle_time_name], fig)
            return fig
        except KeyError:
            logging.error(f"Didn't got any information for {cycle_time_name}")
            logging.error("Are you sure you configured the workflow correctly?")
            return {}

    def draw_all_cycle_time_hist(self, type):
        workflow_keys = list(self.workflow.keys())
        figures = []

        for i in range(len(workflow_keys) - 1):
            wkflow_step = workflow_keys[i]
            fig = self.draw_cycle_time_hist(type, wkflow_step)
            figures.append(fig)

        return figures

    def draw_cfd(self, type):
        cfd = calculator.flow.cfd(self.cycle_data, self.workflow)
        logging.debug(f"Showing CFD for type {type}")
        fig = cfd.plot.line(
            labels={"value": "# of PBI's", "variable": "State", "index": "Date"},
        )
        fig.update_traces(
            fill="tozeroy",
        )
        return fig