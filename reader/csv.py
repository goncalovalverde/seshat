import pandas as pd


def read(csv_file, workflow):
    """Read information from 'csv_file' into dataframe 'cycle_data'
    Interact over 'workflow' and convert the date into datetime
    """

    cycle_data = pd.read_csv(csv_file)
    # Carefull with locale while loading the file!
    cycle_data["Created"] = pd.to_datetime(cycle_data["Created"])
    for item in workflow:
        if item in cycle_data:
            cycle_data[item] = pd.to_datetime(cycle_data[item])
    return cycle_data
