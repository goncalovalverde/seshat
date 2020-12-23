from array import ArrayType
from jira import JIRA
import dateutil.parser
import logging
import reader.cache
import hashlib
from pandas import NaT, DataFrame


class Jira:
    def __init__(self, jira_config: dict, workflow: dict):
        self.jira_config = jira_config
        self.workflow = workflow

        def cache_name(self):
            url = self.jira_config["url"]
            jql_query = self.jira_config["jql_query"]
            workflow = str(self.workflow)
            name_hashed = hashlib.md5((url + jql_query + workflow).encode("utf-8"))
            return name_hashed.hexdigest()

        self.cache = reader.cache.Cache(cache_name(self))

    def get_issue_data(self, issue, issue_data):
        """Iterate over issue data and append it into issue_data array"""
        logging.debug("Getting data for issue " + issue.key)
        issue_data["Key"].append(issue.key)
        issue_data["Type"].append(issue.fields.issuetype.name)
        issue_data["Creator"].append(issue.fields.creator.displayName)

        issue_data["Created"].append(
            dateutil.parser.parse(issue.fields.created).replace(tzinfo=None)
        )
        if self.jira_config.get("story_points_field"):
            issue_data["Story Points"].append(
                getattr(issue.fields, self.jira_config["story_points_field"])
            )

        history_item = {}

        if issue.changelog.total > issue.changelog.maxResults:
            logging.debug(
                f"WARNING: Changelog maxResults {issue.changelog.maxResults}, total {issue.changelog.total}"
            )
        # TODO: [SES-47] deal with pagination of issue if total > maxResults
        for history in issue.changelog.histories:
            items = filter(lambda item: item.field == "status", history.items)
            for item in items:
                history_item[item.toString] = dateutil.parser.parse(
                    history.created
                ).replace(tzinfo=None)

        for workflow_step in self.workflow:
            if workflow_step != "Created":
                issue_data[workflow_step].append(history_item.get(workflow_step, NaT))

    def get_issues(self):
        logging.debug("Getting chunk of issues")

        jira = self.get_jira_instance()
        issues = []
        i = 0
        chunk_size = 100
        while True:
            logging.debug(f"Getting chunk {int(i/chunk_size)+1} of {chunk_size} issues")
            chunk = jira.search_issues(
                self.jira_config["jql_query"],
                expand="changelog",
                maxResults=chunk_size,
                startAt=i,
            )
            i += chunk_size
            issues += chunk.iterable
            if i >= chunk.total:
                break

        return issues

    def get_data(self) -> DataFrame:
        """Retrieve data from jira and return as a Data Frame"""
        logging.debug("Getting data from jira")

        if self.jira_config["cache"] and self.cache.is_valid():
            logging.debug("Getting jira data from cache")
            df_issue_data = self.cache.read()
            return df_issue_data

        logging.debug("Getting info from jira")
        issue_data = {
            "Key": [],
            "Type": [],
            "Story Points": [],
            "Creator": [],
            "Created": [],
        }

        for workflow_step in self.workflow:
            issue_data[workflow_step] = []

        issues = self.get_issues()

        for issue in issues:
            self.get_issue_data(issue, issue_data)

        df_issue_data = DataFrame(issue_data)
        if self.jira_config["cache"]:
            self.cache.write(df_issue_data)

        df_issue_data.fillna(NaT)
        return df_issue_data

    def get_jira_instance(self):
        jira_url = self.jira_config["url"]
        logging.debug("connecting to jira " + jira_url)
        if self.jira_config["auth_method"] == "oauth":
            logging.debug("Connecting to jira via oauth")

            key_cert_data = None
            key_cert = self.jira_config["oauth"]["key_cert_file"]
            logging.debug("Opening Key Cert File " + key_cert)

            with open(key_cert, "r") as key_cert_file:
                key_cert_data = key_cert_file.read()

            oauth_dict = {
                "access_token": self.jira_config["oauth"]["token"],
                "access_token_secret": self.jira_config["oauth"]["token_secret"],
                "consumer_key": self.jira_config["oauth"]["consumer_key"],
                "key_cert": key_cert_data,
            }

            logging.debug("Connecting to jira")
            jira = JIRA(jira_url, oauth=oauth_dict)
        else:
            jira = JIRA(
                jira_url,
                basic_auth=(self.jira_config["username"], self.jira_config["password"]),
            )
        return jira