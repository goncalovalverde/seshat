import reader.jira
import reader.csv
import logging

def read_data(config):
    cycle_data = None

    mode = config["input"]["mode"]

    if mode == "csv":
        cycle_data = reader.csv.read(
            config["input"]["csv_file"], config["Workflow"])
    elif mode == "jira":
        jira = reader.jira.Jira(config["jira"], config["Workflow"])
        cycle_data = jira.get_jira_data()

    return cycle_data

def validate_data(cycle_data,config):
    for workflow_step in config["workflow"]:
        logging(f"No data found for {workflow_step}")
