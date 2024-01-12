from datetime import datetime
import logging
import pandas as pd
from pandas.core.frame import DataFrame
from typing import Dict

class CSV:
    def __init__(self, config: Dict[str, str], workflow: Dict[str, str]) -> None:
        """Initializes the CSV with a specified config and workflow."""
        self.config = config
        self.workflow = workflow

    def get_data(self) -> DataFrame:
        """Read information from 'csv_file' into dataframe 'cycle_data'
        Interact over 'workflow' and convert the date into datetime
        """
        csv_file = self.config.get("file")
        if csv_file is None:
            raise ValueError("No file specified in config.")
        try:
            csv_data = pd.read_csv(csv_file)
        except FileNotFoundError:
            logging.error(f"File {csv_file} not found.")
            raise
        except pd.errors.ParserError:
            logging.error(f"Could not parse file {csv_file}.")
            raise

        # Carefull with locale while loading the file!
        for item in self.workflow:
            if item in csv_data:
                csv_data[item] = pd.to_datetime(csv_data[item])

        return csv_data

    def refresh_data(self, date: datetime) -> DataFrame:
        logging.info("Refreshing CSV data")
        return self.get_data()
