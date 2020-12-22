import gitlab
import dateutil.parser
from pandas import DataFrame, NaT


class Gitlab:
    def __init__(self, gitlab_config: dict, workflow: dict):
        self.gitlab_config = gitlab_config
        self.workflow = workflow

    def get_gitlab_instance(self):
        gl = gitlab.Gitlab(
            self.gitlab_config["url"], private_token=self.gitlab_config["token"]
        )
        gl.auth()

        return gl

    def get_issue_data(self, issue, issue_data):
        issue_data["Key"].append(issue.id)
        issue_data["Type"].append("issue")
        issue_data["Creator"].append(issue.author["name"])
        issue_data["Created"].append(
            dateutil.parser.parse(issue.created_at).replace(tzinfo=None)
        )
        issue_data["Done"].append(
            dateutil.parser.parse(issue.created_at).replace(tzinfo=None)
            if issue.created_at
            else NaT
        )

    def get_issues(self):
        gl = self.get_gitlab_instance()

        if self.gitlab_config.get("project_id"):
            project = gl.projects.get(self.gitlab_config["project_id"])
            issues = project.issues.list()

        elif self.gitlab_config.get("group_id"):
            group = gl.groups.get(self.gitlab_config["group_id"])
            issues = group.issues.list()

        return issues

    def get_data(self):
        issues = self.get_issues()
        issue_data = {"Key": [], "Type": [], "Creator": [], "Created": [], "Done": []}
        for issue in issues:
            self.get_issue_data(issue, issue_data)
        df_issue_data = DataFrame(issue_data)
        return df_issue_data
