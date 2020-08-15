#!/usr/bin/python
import yaml
import pandas as pd
import reader.jira
import reader.csv
import calculator.flow

config_file=open("config.yml")
config=yaml.load(config_file,Loader=yaml.FullLoader)
mode=config["input"]["mode"]


if mode == "csv":
    cycle_data=reader.csv.read_csv(config["input"]["csv_file"],config["Workflow"])
elif mode == "jira":
    jira=reader.jira.Jira(config["jira"],config["Workflow"])
    cycle_data=pd.DataFrame(jira.get_jira_data())

print(cycle_data)

if config["output"]["format"]=="xslx":
    with pd.ExcelWriter(config["output"]["filename"]) as writer:
        cycle_data.to_excel(writer)

print(calculator.flow.throughput(cycle_data))