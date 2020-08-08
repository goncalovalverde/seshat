#!/usr/bin/python
import yaml
import pprint
import pandas as pd
import reader.jira

config_file=open("config.yml")
config=yaml.load(config_file,Loader=yaml.FullLoader)
mode=config["input"]["mode"]


if mode == "csv":
    csv_file=config["input"]["csv_file"]
    cycle=pd.read_csv(csv_file)
elif mode == "jira":
    cycle=pd.DataFrame(reader.jira.get_jira_data(config))

print(cycle)