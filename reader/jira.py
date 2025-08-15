from array import ArrayType
from datetime import datetime
from jira import JIRA
import dateutil.parser
import logging
import numpy as np
NaN = np.nan
import reader.cache
import hashlib
from pandas import NaT, DataFrame, Int8Dtype


class Jira:
    """
    A class to interact with Jira.

    :param jira_config: The Jira configuration
    :type jira_config: dict
    :param workflow: The workflow dictionary
    :type workflow: dict
    """
    def __init__(self, jira_config: dict, workflow: dict):
        self.jira_config = jira_config
        self.workflow = workflow

        def cache_name(self):
            """
            Generate a cache name based on the Jira configuration and workflow.

            :return: The hashed cache name
            :rtype: str
            """
            url = self.jira_config["url"]
            jql_query = self.jira_config["jql_query"]
            workflow = str(self.workflow)
            name_hashed = hashlib.md5((url + jql_query + workflow).encode("utf-8"))
            return name_hashed.hexdigest()

        self.cache = reader.cache.Cache(cache_name(self))

    def get_story_points(self, issue):
        return getattr(issue.fields, self.jira_config["story_points_field"], NaN) if self.jira_config.get("story_points_field") else NaN

    def get_issue_data(self, issue):
        """
        Iterate over issue data and append it into issue_data array.

        :param issue: The issue to get data from
        :type issue: jira.resources.Issue
        :return: The issue data
        :rtype: dict
        """
        logging.debug("Getting data for issue %s", issue.key)
        issue_data = {
            "Key": issue.key,
            "Type": issue.fields.issuetype.name,
            "Creator": issue.fields.creator.displayName,
            "Story Points": self.get_story_points(issue),
            "Created": dateutil.parser.parse(issue.fields.created).replace(tzinfo=None),
        }

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
                issue_data[workflow_step] = history_item.get(workflow_step, NaT)
        return issue_data

    def get_issues(self, jql_query):
        logging.debug("Getting chunk of issues")

        jira = self.get_jira_instance()
        issues = []
        chunk_size = 100
        for i in range(0, jira.search_issues(jql_query, maxResults=0).total, chunk_size):
            logging.debug(f"Getting chunk {int(i/chunk_size)+1} of {chunk_size} issues")
            chunk = jira.search_issues(
                jql_query,
                expand="changelog",
                maxResults=chunk_size,
                startAt=i,
            )
        issues += chunk.iterable

        return issues
    

    def get_data_from_jira(self,jql_query):
        issues = self.get_issues(jql_query)
        issues_data = [self.get_issue_data(issue) for issue in issues]
        df_issues_data = DataFrame(issues_data)
        return df_issues_data

    def get_data(self) -> DataFrame:
        """Retrieve data from jira and return as a Data Frame"""
        logging.info("Getting data from jira")

        if self.jira_config["cache"] and self.cache.is_valid():
            logging.info("Returning jira data from cache")
            df_issue_data = self.cache.read()
            return df_issue_data

        logging.info("Getting info from jira")

        df_issues_data = self.get_data_from_jira(self.jira_config["jql_query"])

        # If Story Points column exists, force Int8Dtype
        # if "Story Points" in df_issues_data:
        #    df_issues_data["Story Points"] = df_issues_data["Story Points"].astype(
        #        "Int64"
        #    )
        if self.jira_config["cache"]:
            self.cache.write(df_issues_data)

        return df_issues_data

    def refresh_data(self, date: datetime) -> DataFrame:
        logging.info("Refreshing data from jira")
        jql_query = f"{self.jira_config['jql_query']} AND UPDATED >= '{date.strftime('%Y/%m/%d')}'"  #

        if self.jira_config["cache"] and self.cache.is_valid():
            logging.info("Geting jira data from cache")
            df_issue_data = self.cache.read()

            df_new_issue_data = self.get_data_from_jira(jql_query)
            df_issue_data = df_issue_data.append(df_new_issue_data)

            # remove duplicates and return only the latest values
            df_issue_data = df_issue_data.drop_duplicates(subset=["Key"], keep="last")

            self.cache.write(df_issue_data)

            return df_issue_data

        return self.get_data()

    def get_jira_instance(self):
        try:
            jira_url = self.jira_config["url"]
            auth_method = self.jira_config["auth_method"]
            logging.debug("Connecting to JIRA %s using %s authentication", jira_url, auth_method)
 
            if auth_method == "oauth": 
                oauth_dict = self.__get_oauth_dict()
                jira = JIRA(jira_url, oauth=oauth_dict)

            elif auth_method == "token":
                jira = JIRA(
                    jira_url,
                    basic_auth=(self.jira_config["username"], self.jira_config["password"]),
                )
            elif auth_method == "cookie":
                jira = JIRA(
                    jira_url,
                    auth=(self.jira_config["username"], self.jira_config["password"]),
                )
            else:
                raise ValueError("Unknown jira auth method " + auth_method)
            return jira
        
        except KeyError as e:
            logging.error(f"Missing configuration key: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to connect to Jira: {e}")
            raise

    def __get_oauth_dict(self):
        key_cert = self.jira_config["oauth"]["key_cert_file"]
        logging.debug("Opening Key Cert File %s", key_cert)
        with open(key_cert, "r") as key_cert_file:
            key_cert_data = key_cert_file.read()

        return {
            "access_token": self.jira_config["oauth"]["token"],
            "access_token_secret": self.jira_config["oauth"]["token_secret"],
            "consumer_key": self.jira_config["oauth"]["consumer_key"],
            "key_cert": key_cert_data,
        }