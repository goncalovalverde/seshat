from datetime import datetime
import logging
import reader.cache
import hashlib
import dateutil.parser
from pandas import DataFrame, NaT
from clubhouse import ClubhouseClient


class Clubhouse:
    def __init__(self, clubhouse_config: dict, workflow: dict) -> None:
        super().__init__()
        self.clubhouse_config = clubhouse_config
        self.project_id = clubhouse_config["project_id"]
        self.workflow = workflow

        def cache_name(self):
            api_key = self.clubhouse_config["api_key"]
            workflow = str(self.workflow)
            name_hashed = hashlib.md5(
                (api_key + self.project_id + workflow).encode("utf-8")
            )
            return name_hashed.hexdigest()

        self.cache = reader.cache.Cache(cache_name(self))

    def get_clubhouse_instance(self) -> ClubhouseClient:
        clubhouse = ClubhouseClient(self.clubhouse_config["api_key"])
        return clubhouse

    def get_story_data(self, story):
        logging.debug("Reading data for story %s", str(story["id"]))
        story_data = {
            "Key": story["id"],
            "Type": story["story_type"],
            "Story Points": story["estimate"],
            "Creator": NaT,
            "Created": dateutil.parser.parse(story["created_at"]).replace(tzinfo=None),
            "Started": (
                dateutil.parser.parse(story["started_at"]).replace(tzinfo=None)
                if story["started"]
                else NaT
            ),
            "Done": (
                dateutil.parser.parse(story["completed_at"]).replace(tzinfo=None)
                if story["completed"]
                else NaT
            ),
        }
        return story_data

    def get_stories(self):
        logging.debug("Getting stories")
        clubhouse = self.get_clubhouse_instance()
        stories = clubhouse.get(f"projects/{self.project_id}/stories")
        return stories

    def get_data(self) -> DataFrame:
        logging.debug("Getting stories from Clubhouse.io")

        if self.clubhouse_config["cache"] and self.cache.is_valid():
            logging.debug("Getting clubhouse.io data from cache")
            df_story_data = self.cache.read()
            return df_story_data

        stories = self.get_stories()

        stories_data = [self.get_story_data(story) for story in stories]

        df_stories_data = DataFrame(stories_data)

        if self.clubhouse_config["cache"]:
            logging.debug("Storing clubhouse.io story data in cache")
            self.cache.write(df_stories_data)

        return df_stories_data

    def refresh_data(self, date: datetime) -> DataFrame:
        # TODO: [SES-56] implement search of new issues instead of just getting everything
        if self.clubhouse_config["cache"] and self.cache.is_valid():
            self.cache.clean()

        return self.get_data()
