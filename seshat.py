#!/usr/bin/python
import yaml
import pandas as pd
import reader.jira
import reader.csv
import calculator.flow
import viewer.team_metrics
import viewer.dash
import logging
import logging.config


with open('log_config.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)
logger.info("Starting seshat. Let's do team magic!")

with open("config.yml", 'r') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
# Add special "issue_type" Total to ensure we can see the total in all graphs
    config["issue_type"].insert(0, "Total")

mode = config["input"]["mode"]

cycle_data = None

if mode == "csv":
    cycle_data = reader.csv.read(
        config["input"]["csv_file"], config["Workflow"])
elif mode == "jira":
    jira = reader.jira.Jira(config["jira"], config["Workflow"])
    cycle_data = jira.get_jira_data()
    cycle_data.fillna(pd.NaT)

print(cycle_data)

throughput = calculator.flow.throughput(cycle_data)

# get the first element of the workflow
# to know where to start calculating the lead time
workflow_keys = list(config["Workflow"].keys())
start = workflow_keys[0]
start = "Created"

cycle_data = calculator.flow.lead_time(cycle_data, start)

for i in range(len(workflow_keys)-1):
    start = workflow_keys[i]
    end = workflow_keys[i+1]
    calculator.flow.cycle_time(cycle_data, start, end)

net_flow = calculator.flow.net_flow(cycle_data, "Total")

team_metrics = viewer.team_metrics.Team_Metrics(cycle_data, throughput, config)
dash = viewer.dash.Dash(team_metrics, config)

if config["output"]["format"] == "xlsx":
    with pd.ExcelWriter(config["output"]["filename"]) as writer:
        logging.debug("Writing cycle_data to " + config["output"]["filename"])
        cycle_data.to_excel(writer)

if __name__ == '__main__':
    dash.run()
