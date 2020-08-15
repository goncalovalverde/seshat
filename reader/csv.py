import pandas as pd


def read_csv(csv_file, workflow):
    cycle_data = pd.read_csv(csv_file)
    cycle_data["Created"] = pd.to_datetime(cycle_data["Created"])
    for item in workflow:
        if item in cycle_data:
            cycle_data[item] = pd.to_datetime(cycle_data[item])
    return cycle_data
