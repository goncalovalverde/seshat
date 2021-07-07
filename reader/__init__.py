from pandas.core.frame import DataFrame
import reader.jira
import reader.csv
import reader.trello
import reader.clubhouse
import reader.gitlab
import logging


class Reader:
    def __init__(self, config):
        """Based in 'config' decide if we need to import data from a csv file, trello, jira, clubhouse or gitlab
        and then invoke the right method.
        """
        self.config = config
        self.mode = config["mode"]

        if self.mode == "csv":
            self.reader = reader.csv.CSV(config["csv"], config["Workflow"])
        elif self.mode == "jira":
            self.reader = reader.jira.Jira(config["jira"], config["Workflow"])
        elif self.mode == "trello":
            self.reader = reader.trello.Trello(config["trello"], config["Workflow"])
        elif self.mode == "clubhouse":
            self.reader = reader.clubhouse.Clubhouse(
                config["clubhouse"], config["Workflow"]
            )
        elif self.mode == "gitlab":
            self.reader = reader.gitlab.Gitlab(config["gitlab"], config["Workflow"])
        else:
            raise ValueError(f"Invalid mode {self.mode}")

    def get_data(self) -> DataFrame:
        """
        Read the information into a dataframe
        """
        return self.reader.get_data()

    def refresh_data(self) -> DataFrame:
        return self.reader.refresh_data()


def validate_data(cycle_data, config):
    for workflow_step in config["workflow"]:
        logging.info(f"No data found for {workflow_step}")
