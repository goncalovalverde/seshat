import pandas as pd

def read_csv(csv_file):
    cycle_data=pd.read_csv(csv_file)
    cycle_data["Done"]=pd.to_datetime(cycle_data["Done"])
    return cycle_data