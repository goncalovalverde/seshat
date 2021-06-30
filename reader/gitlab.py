import gitlab
import dateutil.parser
import reader.cache
import hashlib
import logging
from pandas import DataFrame, NaT
from datetime import datetime


class Gitlab:
    def __init__(self, gitlab_config: dict, workflow: dict):
        self.gitlab_config = gitlab_config
        self.workflow = workflow

        def cache_name(self):
            token = self.gitlab_config["token"]
            workflow = str(self.workflow)
            url = self.gitlab_config["url"]
            id = (
                self.gitlab_config.get("project_id")
                if self.gitlab_config.get("project_id")
                else self.gitlab_config.get("group_id")
            )
            name_hashed = hashlib.md5(
                (token + url + workflow + str(id)).encode("utf-8")
            )
            return name_hashed.hexdigest()

        self.cache = reader.cache.Cache(cache_name(self))

    def get_gitlab_instance(self):
        gl = gitlab.Gitlab(
            self.gitlab_config["url"], private_token=self.gitlab_config["token"]
        )
        gl.auth()

        return gl

    def get_issue_data(self, issue):
        issue_data = {
            "Key": issue.id,
            "Type": "issue",
            "Creator": issue.author["name"],
            "Created": dateutil.parser.parse(issue.created_at).replace(tzinfo=None),
            "Done": (
                dateutil.parser.parse(issue.created_at).replace(tzinfo=None)
                if issue.created_at
                else NaT
            ),
        }
        return issue_data

    def get_issues(self):
        gl = self.get_gitlab_instance()

        if self.gitlab_config.get("project_id"):
            project = gl.projects.get(self.gitlab_config["project_id"])
            issues = project.issues.list()

        elif self.gitlab_config.get("group_id"):
            group = gl.groups.get(self.gitlab_config["group_id"])
            issues = group.issues.list()

        else:
            raise Exception("No valid project_id or group_id found!")

        return issues

    def get_data(self) -> DataFrame:

        if self.gitlab_config["cache"] and self.cache.is_valid():
            logging.debug("Getting gitlab data from cache")
            df_issue_data = self.cache.read()
            return df_issue_data

        issues = self.get_issues()

        # issue_data = {"Key": [], "Type": [], "Creator": [], "Created": [], "Done": []}
        issues_data = [self.get_issue_data(issue) for issue in issues]

        df_issues_data = DataFrame(issues_data)

        if self.gitlab_config["cache"]:
            logging.debug("Storing gitlab issue data in cache")
            self.cache.write(df_issues_data)

        return df_issues_data

    def refresh_data(self, date: datetime) -> DataFrame:
        if self.gitlab_config["cache"] and self.cache.is_valid():
            self.cache.clean()

        return self.get_data()
