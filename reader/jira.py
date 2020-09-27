from jira import JIRA
import dateutil.parser
import logging
from pandas import NaT

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
            history_item[workflow_step] = NaT

        for history in issue.changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    history_item[item.toString] = dateutil.parser.parse(history.created).replace(tzinfo=None)
                    
        
        for workflow_step in self.workflow:
            issue_data[workflow_step].append(history_item[workflow_step])

    def get_issues(self):

        jira = self.get_jira_instance()
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
        logging.debug("Getting info from jira")
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

    def get_jira_instance(self):
        jira_url = self.jira_config["url"]
        logging.debug("connecting to jira " + jira_url)
        if self.jira_config["auth_method"] == "oauth":
            logging.debug("Connecting to jira via oauth")
            
            key_cert_data = None
            key_cert = self.jira_config["oauth"]["key_cert_file"]
            logging.debug("Opening Key Cert File " + key_cert )
            
            with open(key_cert, 'r') as key_cert_file:
                key_cert_data = key_cert_file.read()

            oauth_dict = {
                'access_token': self.jira_config["oauth"]["token"],
                'access_token_secret': self.jira_config["oauth"]["token_secret"],
                'consumer_key': self.jira_config["oauth"]["consumer_key"],
                'key_cert': key_cert_data
            }

            jira = JIRA(jira_url,oauth=oauth_dict)
        else:
            jira = JIRA(
                jira_url,
                basic_auth=(self.jira_config["username"], self.jira_config["password"])
            )
        return jira