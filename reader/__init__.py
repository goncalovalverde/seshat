from pandas.core.frame import DataFrame
import reader.jira
import reader.csv
import reader.trello
import reader.clubhouse
import reader.gitlab
import logging


class Reader:
    def __init__(self, config):
        """
        Based on 'config', decide if we need to import data from a csv file, trello, jira, clubhouse or gitlab
        and then invoke the right method.

        :param config: The configuration dictionary
        :type config: dict
        """
        self.config = config
        self.mode = config.get("mode")

        reader_classes = {
            "csv": reader.csv.CSV,
            "jira": reader.jira.Jira,
            "trello": reader.trello.Trello,
            "clubhouse": reader.clubhouse.Clubhouse,
            "gitlab": reader.gitlab.Gitlab,
        }

        try:
            ReaderClass = reader_classes[self.mode]
            self.reader = ReaderClass(config[self.mode], config["Workflow"])
        except KeyError:
            raise ValueError(f"Invalid mode {self.mode}")

    def get_data(self) -> DataFrame:
        """
        Read the information into a dataframe and return it

        :return: The DataFrame with the data
        :rtype: DataFrame
        """
        return self.reader.get_data()

    def refresh_data(self) -> DataFrame:
        """
        Refresh the data and return it

        :return: The DataFrame with the refreshed data
        :rtype: DataFrame
        """        
        return self.reader.refresh_data()


    def validate_data(cycle_data, config):
        """
        Validate the cycle data against the workflow in the config.

        :param cycle_data: The cycle data
        :type cycle_data: DataFrame
        :param config: The configuration dictionary
        :type config: dict
        """
        try:
            for workflow_step in config["workflow"]:
                if workflow_step not in cycle_data.columns:
                    logging.info(f"No data found for {workflow_step}")
        except KeyError:
            logging.error("No workflow found in config")
