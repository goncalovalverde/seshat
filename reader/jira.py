from jira import JIRA
import dateutil.parser

def get_issue_data(issue,issue_data,config):
    issue_data["Key"].append(issue.key)
    issue_data["Type"].append(issue.fields.issuetype.name)
    issue_data["Created"].append(dateutil.parser.parse(issue.fields.created).replace(tzinfo=None))

    history_item={}
    for workflow_step in config["Workflow"]:
        history_item[workflow_step]="0"

    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == 'status':
                history_item[item.toString]=dateutil.parser.parse(history.created).replace(tzinfo=None)
    
    for workflow_step in config["Workflow"]:
        issue_data[workflow_step].append(history_item[workflow_step])

def get_issues(config):
    jira = JIRA(
        config["jira"]["url"],
        basic_auth=(config["jira"]["username"],config["jira"]["password"])
    )
    
    startAt=0

    issues = jira.search_issues(config["jql_query"],expand="changelog",maxResults=100,startAt=startAt)
    return issues

def get_jira_data(config):
    issue_data={
        "Key": [],
        "Type": [], 
        "Created": []
    }

    for workflow_step in config["Workflow"]:
        issue_data[workflow_step]=[]

    issues=get_issues(config)    

    for issue in issues:
        get_issue_data(issue,issue_data,config)

    return issue_data
