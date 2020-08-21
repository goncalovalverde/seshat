#!/usr/bin/python
import yaml
import pandas as pd
import reader.jira
import reader.csv
import calculator.flow
import viewer.team_metrics
import logging
import logging.config


with open('log_config.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)
logger.info("Starting seshat. Let's do team magic!")

with open("config.yml",'r') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)

mode = config["input"]["mode"]

if mode == "csv":
    cycle_data = reader.csv.read(
        config["input"]["csv_file"], config["Workflow"])
elif mode == "jira":
    jira = reader.jira.Jira(config["jira"], config["Workflow"])
    cycle_data = pd.DataFrame(jira.get_jira_data())

if config["output"]["format"] == "xslx":
    with pd.ExcelWriter(config["output"]["filename"]) as writer:
        cycle_data.to_excel(writer)

throughput = calculator.flow.throughput(cycle_data)
throughput = calculator.flow.defect_percentage(throughput)
cycle_data = calculator.flow.lead_time(cycle_data)
net_flow = calculator.flow.net_flow(cycle_data)

print(cycle_data)

team_metrics = viewer.team_metrics.Team_Metrics(cycle_data, throughput, net_flow)
team_metrics.show_dash()
