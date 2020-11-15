from pandas.core.frame import DataFrame
import reader.jira
import reader.csv
import reader.trello
import logging


def read_data(config):
    """Based in 'config' decide if we need to import data from a csv file or from jira
    and then invoke the right method.
    Read the information into a dataframe called 'cycle_data'
    """
    cycle_data = None

    mode = config["input"]["mode"]

    if mode == "csv":
        cycle_data = reader.csv.read(config["input"]["csv_file"], config["Workflow"])
    elif mode == "jira":
        jira = reader.jira.Jira(config["jira"], config["Workflow"])
        cycle_data = jira.get_data()
    elif mode == "trello":
        trello = reader.trello.Trello(config["trello"], config["Workflow"])
        cycle_data = trello.get_cards()
    else:
        logging.error("Don't know what to do for mode " + mode)
        return {}

    return cycle_data


def validate_data(cycle_data, config):
    for workflow_step in config["workflow"]:
        logging.info(f"No data found for {workflow_step}")
