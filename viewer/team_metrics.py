import pandas as pd
import numpy as np


def show_throughput(cycle_data):
    pd.options.plotting.backend = "plotly"
    fig=cycle_data.plot.line()
    fig.show()
    results = px.get_trendline_results(fig)
