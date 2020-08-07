#!/usr/bin/python
import yaml
import pprint
from jira import JIRA
import pandas as pd
import dateutil.parser

config_file=open("config.yml")
config=yaml.load(config_file,Loader=yaml.FullLoader)
mode=config["input"]["mode"]
csv_file=config["input"]["csv_file"]


def get_issue_data(issue,issue_data):

    issue_data["Key"].append(issue.key)
    issue_data["Type"].append(issue.fields.issuetype.name)
    issue_data["Created"].append(dateutil.parser.parse(issue.fields.created))

    history_item={}
    for workflow_step in config["Workflow"]:
        history_item[workflow_step]="0"


    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == 'status':
                history_item[item.toString]=dateutil.parser.parse(history.created)
    
    for workflow_step in config["Workflow"]:
        issue_data[workflow_step].append(history_item[workflow_step])

def get_issues():
    jira = JIRA(
        config["jira"]["url"],
        basic_auth=(config["jira"]["username"],config["jira"]["password"])
    )

    query_options = {
        "expand": 'changelog',
        "max_results": 100
    }
    issues = jira.search_issues(config["jql_query"],expand="changelog")
    return issues


if mode == "csv":
    cycle=pd.read_csv(csv_file)
elif mode == "jira":

    issue_data={
        "Key": [],
        "Type": [], 
        "Created": []
    }

    for workflow_step in config["Workflow"]:
        issue_data[workflow_step]=[]

    issues=get_issues()    

    for issue in issues:
        get_issue_data(issue,issue_data)

    cycle=pd.DataFrame(issue_data)

print(cycle)