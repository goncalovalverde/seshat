import pandas as pd
from pandas.core.frame import DataFrame


class CSV:
    def __init__(self, config: dict, workflow: dict) -> None:
        super().__init__()
        self.config = config
        self.workflow = workflow

    def get_data(self) -> DataFrame:
        """Read information from 'csv_file' into dataframe 'cycle_data'
        Interact over 'workflow' and convert the date into datetime
        """
        csv_file = self.config["file"]
        cycle_data = pd.read_csv(csv_file)
        # Carefull with locale while loading the file!
        for item in self.workflow:
            if item in cycle_data:
                cycle_data[item] = pd.to_datetime(cycle_data[item])

        return cycle_data
