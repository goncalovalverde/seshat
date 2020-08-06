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


def get_cycle(issue,issue_data):

    issue_data["Key"].append(issue["key"])
    issue_data["Type"].append(issue["fields"]["issuetype"]["name"])
    created=dateutil.parser.parse(issue["fields"]["created"])
    issue_data["Created"].append(created)

    history_item={}
    for workflow_step in config["Workflow"]:
        history_item[workflow_step]="0"


    for history in issue["changelog"]["histories"]:
        for item in history["items"]:
            if item["field"] == 'status':
                item_created=dateutil.parser.parse(history["created"])
                history_item[item["toString"]]=item_created
                #print('Date:' + history["created"] + ' From:' + item["fromString"] + ' To:' + item["toString"])
    
    for workflow_step in config["Workflow"]:
        issue_data[workflow_step].append(history_item[workflow_step])


#pprint.pprint(issues["issues"])~

issue_data={
    "Key": [],
    "Type": [], 
    "Created": []
}

for workflow_step in config["Workflow"]:
    issue_data[workflow_step]=[]

if mode == "csv":
    cycle=pd.read_csv(csv_file)
elif mode == "jira":
    jira = Jira(
        url=config["jira"]["url"],
        username=config["jira"]["username"],
        password=config["jira"]["password"])

    issues = jira.jql(config["jql_query"],expand='changelog')

    for issue in issues["issues"]:
        get_cycle(issue,issue_data)
    cycle=pd.DataFrame(issue_data)

print(cycle)