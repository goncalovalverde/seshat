from pandas.core.frame import DataFrame
import reader.jira
import reader.csv
import reader.trello
import reader.clubhouse
import reader.gitlab
import logging


class Reader:
    def __init__(self, config):
        self.config = config
        self.mode = config["mode"]


def get_data(config):
    """Based in 'config' decide if we need to import data from a csv file, trello, jira, clubhouse or gitlab
    and then invoke the right method.
    Read the information into a dataframe called 'cycle_data'
    """
    cycle_data = None

    mode = config["mode"]

    if mode == "csv":
        csv = reader.csv.CSV(config["csv"], config["Workflow"])
        cycle_data = csv.get_data()
    elif mode == "jira":
        jira = reader.jira.Jira(config["jira"], config["Workflow"])
        cycle_data = jira.get_data()
    elif mode == "trello":
        trello = reader.trello.Trello(config["trello"], config["Workflow"])
        cycle_data = trello.get_data()
    elif mode == "clubhouse":
        clubhouse = reader.clubhouse.Clubhouse(config["clubhouse"], config["Workflow"])
        cycle_data = clubhouse.get_data()
    elif mode == "gitlab":
        gitlab = reader.gitlab.Gitlab(config["gitlab"], config["Workflow"])
        cycle_data = gitlab.get_data()
    else:
        logging.error("Don't know what to do for mode %s", mode)
        return {}

    return cycle_data


def validate_data(cycle_data, config):
    for workflow_step in config["workflow"]:
        logging.info(f"No data found for {workflow_step}")
