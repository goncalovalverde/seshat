#!/usr/bin/python
import yaml
import pprint
from atlassian import Jira
import pandas as pd
import dateutil.parser

config_file=open("config.yml")
config=yaml.load(config_file,Loader=yaml.FullLoader)
mode=config["input"]["mode"]
csv_file=config["input"]["csv_file"]


def get_cycle(issue):
    print("-----")
    print(issue["key"])
    pprint.pprint(issue["fields"]["created"])

    for history in issue["changelog"]["histories"]:
        for item in history["items"]:
            if item["field"] == 'status':
                print('Date:' + history["created"] + ' From:' + item["fromString"] + ' To:' + item["toString"])
#                pprint.pprint(item)


#pprint.pprint(issues["issues"])

if mode == "csv":
    cycle=pd.read_csv(csv_file)
elif mode == "jira":
    jira = Jira(
        url=config["jira"]["url"],
        username=config["jira"]["username"],
        password=config["jira"]["password"])

    issues = jira.jql(config["jql_query"],expand='changelog')

    for issue in issues["issues"]:
        get_cycle(issue)

print(cycle)