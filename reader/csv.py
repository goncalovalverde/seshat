import pandas as pd
from pandas.core.frame import DataFrame


def read(config: dict, workflow: dict) -> DataFrame:
    """Read information from 'csv_file' into dataframe 'cycle_data'
    Interact over 'workflow' and convert the date into datetime
    """
    csv_file = config["file"]
    cycle_data = pd.read_csv(csv_file)
    # Carefull with locale while loading the file!
    for item in workflow:
        if item in cycle_data:
            cycle_data[item] = pd.to_datetime(cycle_data[item])
    return cycle_data
