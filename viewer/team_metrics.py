from array import ArrayType
from typing import List
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import calculator.flow
import calculator.tools
import logging
import viewer.tools
import reader


# TODO: refactor to remove cycle_data and throughput to invocation of internal
# methods and use the class properties instead
class Team_Metrics:
    # def __init__(self, cycle_data, config):
    def __init__(self, data_reader):

        self.data_reader = data_reader
        self.config = data_reader.config
        self.cycle_data = calculator.flow.cycle_data(
            data_reader.get_data(), self.config
        )
        # self.cycle_data = cycle_data

        self.workflow = self.config["Workflow"]

        # Extract the beggining and end of the workflow
        self.start_column = list(self.workflow.keys())[0]
        self.end_column = list(self.workflow.keys())[-1]

        self.throughput = calculator.flow.throughput(self.cycle_data, self.end_column)

        self.name = self.config["name"]
        self.has_story_points = True if "Story Points" in self.cycle_data else False

        self.pbi_types = self.cycle_data["Type"].unique().tolist()
        # Append pseudo issue type "Total"
        self.pbi_types.insert(0, "Total")

        pd.options.plotting.backend = "plotly"

    def draw_throughput(self, pbi_type: str):
        logging.debug("Showing throughput graph for %s", pbi_type)
        throughput = self.throughput
        throughput = throughput.resample("W").sum()

        if pbi_type == "all":
            fig = throughput.plot.line(
                title="Throughput : how many PBI's delivered",
                labels={"value": "Throughput", "variable": "Issue Type"},
            )
        else:
            fig = throughput[pbi_type].plot.line(
                labels={"value": "Throughput"}, text=throughput[pbi_type]
            )

        fig.update_traces(textposition="top center")

        if pbi_type != "all":
            fig.update_layout(
                title='Productivity - How Much - "Do Lots"', showlegend=False
            )

            fig = viewer.tools.add_trendline(throughput, fig, pbi_type)

        return fig

    def add_velocity(self, fig):
        velocity = (
            calculator.flow.velocity(self.cycle_data, self.end_column)
            .resample("W")
            .sum()
        )
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

    def draw_velocity(self, pbi_type: str):
        velocity = (
            calculator.flow.velocity(self.cycle_data, self.end_column)
            .resample("W")
            .sum()
        )
        fig = velocity[pbi_type].plot.line()

        fig.update_layout(
            title="Velocity : How much story points delivered?",
            yaxis={"title": "Story Points"},
        )

        fig = viewer.tools.add_trendline(velocity, fig, "Total")
        return fig

    def draw_story_points(self):
        try:
            story_points = (
                calculator.flow.story_points(self.cycle_data, self.end_column)
                .resample("W")
                .sum()
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

    def draw_lead_time(self, pbi_type: str):
        lead_time = calculator.flow.avg_lead_time(
            self.cycle_data, pbi_type, self.end_column
        )
        fig = lead_time.plot.line()
        fig.update_layout(
            title='Responsiveness - How Fast - "Do it Fast"',
            showlegend=False,
            yaxis={"title": "Lead Time Avg"},
        )
        fig = viewer.tools.add_trendline(lead_time, fig, "Lead Time")
        return fig

    def draw_defect_percentage(self, pbi_type: str):
        """Generate chart with the defect percentage (total done PBI's vs total done bugs)

        :param pbi_type: Type of PBI (Product Backlog Item)
        :type pbi_type: str
        :return: [description]
        :rtype: [type]
        """
        throughput = self.throughput
        throughput = calculator.flow.defect_percentage(throughput, pbi_type)
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

    def draw_net_flow(self, pbi_type: str):
        """Creates chart for the Net Flow of a specific PBI or the total
        Net Flow = PBI done - PBI created

        :param pbi_type: The type of PBI
        :type pbi_type: str
        :return: Plotly chart with the PBI
        :rtype: Plotly Figure
        """
        logging.debug("Drawing Net Flow")

        net_flow = calculator.flow.net_flow(
            self.cycle_data, self.start_column, self.end_column, pbi_type
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

    def draw_wip(self, pbi_type: str):
        """Generate Chart with the WIP for a specific PBI type or the total

        :param pbi_type: Type of PBI (can be total to draw sum of all)
        :type pbi_type: str
        :return: The chart with the WIP
        :rtype: Plottly Figure
        """

        wip = calculator.flow.net_flow(
            self.cycle_data, self.start_column, self.end_column, pbi_type
        )
        fig = wip["WIP"].plot.bar()
        fig.update_layout(
            title="Work in Progress",
            showlegend=False,
            xaxis={"title": "Week"},
            yaxis={"title": "WIP"},
        )
        return fig

    def draw_start_stop(self, pbi_type: str):
        start = calculator.tools.group_by_date(self.cycle_data, self.start_column)
        start = start.resample("W").sum()
        end = calculator.tools.group_by_date(self.cycle_data, self.end_column)
        end = end.resample("W").sum()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=start.index, y=start[pbi_type], mode="lines", name=self.start_column
            )
        )
        fig.add_trace(
            go.Scatter(x=end.index, y=end[pbi_type], mode="lines", name=self.end_column)
        )

        fig.update_layout(legend_xanchor="left", legend_x=0.01, title="Started vs Done")
        return fig

    def draw_lead_time_hist(self, pbi_type):
        lead_time = self.cycle_data[[self.end_column, "Type", "Lead Time"]].copy()
        if pbi_type != "Total":
            lead_time = lead_time.loc[lead_time["Type"] == pbi_type]

        fig = lead_time["Lead Time"].plot.hist()
        fig.update_traces(xbins_size=1)
        fig.update_layout(
            title="Lead Time " + pbi_type,
            showlegend=False,
            yaxis={"title": "Lead time"},
            xaxis={"title": "days"},
        )

        fig = viewer.tools.add_percentile(lead_time["Lead Time"], fig)
        return fig

    def draw_cycle_time_hist(self, pbi_type: str, wkflow_step: str):
        """Generate chart with the cycle time histogram for that PBI Type and Workflow step

        :param pbi_type: The PBI to be used (can be "Total" to return the sum of all)
        :type pbi_type: str
        :param wkflow_step: The Workflow Step
        :type wkflow_step: str
        :return: Graphic of the Cycle Time. Can be blank if an exeption occured (no valid Workflow Step)
        :rtype: [type]
        """
        cycle_data = self.cycle_data
        cycle_time_name = "Cycle Time " + wkflow_step
        logging.debug(f"Showing histogram for {cycle_time_name}")

        try:
            cycle_time = cycle_data[[self.end_column, "Type", cycle_time_name]].copy()
            if pbi_type != "Total":
                cycle_time = cycle_time.loc[cycle_time["Type"] == pbi_type]

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

    def draw_all_cycle_time_hist(self, pbi_type: str) -> List:
        """Generate all Cycle Time Histograms for all steps in the Workflow for a PBI type

        :param pbi_type: The PBI type to generate
        :type pbi_type: str
        :return: Returns a List with all the Cycle Time Histogram Charts
        :rtype: List
        """
        workflow_keys = list(self.workflow.keys())
        figures = []

        for i in range(len(workflow_keys) - 1):
            wkflow_step = workflow_keys[i]
            fig = self.draw_cycle_time_hist(pbi_type, wkflow_step)
            figures.append(fig)

        return figures

    def draw_cfd(self, pbi_type: str):
        cfd = calculator.flow.cfd(self.cycle_data, self.workflow)
        logging.debug(f"Showing CFD for type {pbi_type}")
        fig = cfd.plot.line(
            labels={"value": "# of PBI's", "variable": "State", "index": "Date"},
        )
        fig.update_traces(
            fill="tozeroy",
        )
        return fig

    def refresh(self, mode: str = "all"):
        self.cycle_data = calculator.flow.cycle_data(
            self.data_reader.refresh_data(), self.config
        )
        return
