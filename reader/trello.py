from trello import TrelloClient
from pandas import NaT, DataFrame, isnull
import reader.cache
import hashlib
import logging


class Trello:
    def __init__(self, trello_config, workflow):
        self.trello_config = trello_config
        self.workflow = workflow

        def cache_name(self):
            board = self.trello_config["board_id"]
            workflow = str(self.workflow)
            name_hashed = hashlib.md5((board + workflow).encode("utf-8"))
            return name_hashed.hexdigest()

        self.cache = reader.cache.Cache(cache_name(self))

    def get_trello_instance(self):
        logging.info("Getting Trello client info")
        client = TrelloClient(
            api_key=self.trello_config["api_key"],
            api_secret=self.trello_config["api_secret"],
        )

        return client

    def get_cards(self):
        """ Retrieve card info from Trello """

        if self.trello_config["cache"] and self.cache.is_valid():
            logging.debug("Getting Trello info cached ")
            df_issue_data = self.cache.read()
            return df_issue_data

        logging.debug("Getting trello cards info")
        client = self.get_trello_instance()
        all_boards = client.list_boards()
        board = client.get_board(self.trello_config["board_id"])
        cards = board.all_cards()
        card_data = {"Key": [], "Name": [], "Type": [], "Created": [], "Done": []}

        for card in cards:
            self.get_card_data(card, card_data)

        df_card_data = DataFrame(card_data)

        if self.trello_config["cache"]:
            logging.debug("Writing card data to cache")
            self.cache.write(df_card_data)

        return df_card_data

    def get_card_data(self, card, card_data):
        if card.get_list().name in self.trello_config["ignore"]:
            logging.debug(f"Card in ignored list {card.get_list().name}")
            return

        logging.debug(f"Getting data for card {card.id} in list {card.get_list().name}")
        card_data["Key"].append(card.id)
        card_data["Name"].append(card.name)
        card_data["Created"].append(card.created_date.replace(tzinfo=None))
        card_data["Type"].append("Card")
        done = NaT

        for movement in card.list_movements():
            if movement["destination"]["name"] == self.trello_config["done_column"]:
                done = movement["datetime"].replace(tzinfo=None)
                logging.debug("Got done date: " + str(done))

        # If card was not moved to done column(s) but was already closed (archived)
        if isnull(done) and card.closed:
            done = card.dateLastActivity.replace(tzinfo=None)
            logging.debug(f"Card is closed. using last activity date: {done}")

        card_data["Done"].append(done)
