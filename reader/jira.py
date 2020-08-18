from jira import JIRA
import dateutil.parser
import pprint
from math import nan

class Jira:
    def __init__(self, jira_config, workflow):
        self.jira_config = jira_config
        self.workflow = workflow

    def get_issue_data(self, issue, issue_data):
        issue_data["Key"].append(issue.key)
        issue_data["Type"].append(issue.fields.issuetype.name)
        issue_data["Created"].append(dateutil.parser.parse(issue.fields.created).replace(tzinfo=None))

        history_item = {}
        for workflow_step in self.workflow:
            history_item[workflow_step]=nan

        for history in issue.changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    history_item[item.toString]=dateutil.parser.parse(history.created).replace(tzinfo=None)
        
        for workflow_step in self.workflow:
            issue_data[workflow_step].append(history_item[workflow_step])

    def get_issues(self):
        jira = JIRA(
            self.jira_config["url"],
            basic_auth=(self.jira_config["username"], self.jira_config["password"])
        )
        
        issues = []
        i = 0
        chunk_size = 100
        while True:
            chunk = jira.search_issues(
                self.jira_config["jql_query"],
                expand="changelog",
                maxResults=chunk_size, startAt=i)
            i += chunk_size
            issues += chunk.iterable
            if i >= chunk.total:
                break

        return issues

    def get_jira_data(self):
        issue_data = {
            "Key": [],
            "Type": [],
            "Created": []
        }

        for workflow_step in self.workflow:
            issue_data[workflow_step] = []

        issues = self.get_issues()   

        for issue in issues:
            self.get_issue_data(issue, issue_data)

        return issue_data
