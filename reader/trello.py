from trello import TrelloClient
from pandas import NaT, DataFrame, isnull
import reader.cache
import hashlib
import logging
from datetime import datetime


class Trello:
    """
    A class to interact with Trello.

    :param trello_config: The Trello configuration
    :type trello_config: dict
    :param workflow: The workflow dictionary
    :type workflow: dict
    """
    def __init__(self, trello_config, workflow):
        self.trello_config = trello_config
        self.workflow = workflow
        self.done_column = list(self.workflow.keys())[-1]

        def cache_name(self):
            board = self.trello_config["board_id"]
            workflow = str(self.workflow)
            name_hashed = hashlib.md5((board + workflow).encode("utf-8"))
            return name_hashed.hexdigest()

        self.cache = reader.cache.Cache(cache_name(self))

    def get_trello_instance(self) -> TrelloClient:
        """
        Get a Trello client instance.

        :return: The Trello client
        :rtype: TrelloClient
        """
        logging.info("Getting Trello client info")
        client = TrelloClient(
            api_key=self.trello_config["api_key"],
            api_secret=self.trello_config["api_secret"],
        )

        return client

    def get_cards(self):
        """
        Get all cards from the Trello board.

        :return: The list of cards
        :rtype: list
        """
        client = self.get_trello_instance()
        board = client.get_board(self.trello_config["board_id"])
        cards = board.all_cards()
        return cards

    def get_card_data(
        self,
        card,
    ):
        """Read card data information and return it as a card_data dict"""
        if card.get_list().name in self.trello_config["ignore"]:
            logging.debug(f"Card in ignored list {card.get_list().name}")
            return

        logging.debug(f"Getting data for card {card.id} in list {card.get_list().name}")
        card_data = {
            "Key": card.id,
            "Name": card.name,
            "Type": "Card",
            "Created": card.created_date.replace(tzinfo=None),
        }

        movement_item = {}

        for movement in card.list_movements():
            movement_item[movement["destination"]["name"]] = movement[
                "datetime"
            ].replace(tzinfo=None)
            logging.debug(
                f'Got {movement["destination"]["name"]} date: {str(movement["datetime"])}'
            )

        # If card was not moved to done column(s) but was already closed (archived)
        if isnull(movement_item.get(self.done_column, NaT)) and card.closed:
            movement_item[self.done_column] = card.dateLastActivity.replace(tzinfo=None)
            logging.debug(
                f"Card is closed. using last activity date: {movement_item[self.done_column]}"
            )

        for workflow_step in self.workflow:
            if workflow_step != "Created":
                card_data[workflow_step] = movement_item.get(workflow_step, NaT)
        return card_data

    def get_data(self) -> DataFrame:
        """ Retrieve card info from Trello """
        """ Returns results as a pandas DataFrame"""

        if self.trello_config["cache"] and self.cache.is_valid():
            logging.debug("Getting Trello info cached ")
            df_issue_data = self.cache.read()
            return df_issue_data

        logging.debug("Getting trello cards info")
        cards = self.get_cards()

        cards_data = []
        for card in cards:
            if card_data := self.get_card_data(card):
                cards_data.append(card_data)

        df_cards_data = DataFrame(cards_data)

        if self.trello_config["cache"]:
            logging.debug("Writing card data to cache")
            self.cache.write(df_cards_data)

        return df_cards_data

    def refresh_data(self, date: datetime) -> DataFrame:
        if self.trello_config["cache"] and self.cache.is_valid():
            self.cache.clean()

        return self.get_data()