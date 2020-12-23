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

    def get_story_data(self, story, story_data):
        logging.debug("Reading data for story " + str(story["id"]))
        story_data["Key"].append(story["id"])
        story_data["Type"].append(story["story_type"])
        story_data["Story Points"].append(story["estimate"])
        story_data["Creator"].append(NaT)
        story_data["Created"].append(
            dateutil.parser.parse(story["created_at"]).replace(tzinfo=None)
        )
        story_data["Started"].append(
            dateutil.parser.parse(story["started_at"]).replace(tzinfo=None)
            if story["started"]
            else NaT
        )
        story_data["Done"].append(
            dateutil.parser.parse(story["completed_at"]).replace(tzinfo=None)
            if story["completed"]
            else NaT
        )

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
        story_data = {
            "Key": [],
            "Type": [],
            "Story Points": [],
            "Creator": [],
            "Created": [],
            "Started": [],
            "Done": [],
        }

        for story in stories:
            self.get_story_data(story, story_data)

        df_story_data = DataFrame(story_data)

        if self.clubhouse_config["cache"]:
            logging.debug("Storing clubhouse.io story data in cache")
            self.cache.write(df_story_data)

        return df_story_data