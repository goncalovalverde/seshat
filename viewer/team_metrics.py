import pandas as pd


def show_throughput(cycle_data):
    pd.options.plotting.backend = "plotly"
    fig = cycle_data.plot.line()
    fig.show()


def show_lead_time(cycle_data):
    pd.options.plotting.backend = "plotly"
    fig = cycle_data.plot.scatter(
        x=cycle_data["Done"], y=cycle_data["Lead Time"])
    fig.show()


def show_defect_percentage(throughput):
    pd.options.plotting.backend = "plotly"
    fig = throughput["Defect Percentage"].plot()
    fig.show()


def show_net_flow(cycle_data):
    pd.options.plotting.backend = "plotly"
    fig = cycle_data["Net Flow"].plot.bar()
    fig.show()