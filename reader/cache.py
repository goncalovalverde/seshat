import os
import pandas as pd
import logging
import config


class Cache:
    def __init__(self, filename):
        cache_dir = config.get("cache_dir")
        self.file = f"{cache_dir}/seshat_cache_{filename}.pkl"
        logging.info("Initializing Cache")

    def write(self, data):
        logging.debug("Writing to cache " + self.file)
        data.to_pickle(self.file)

    def read(self):
        logging.debug("Reading from cache " + self.file)
        data = pd.read_pickle(self.file)
        return data

    def clean(self):
        logging.debug("Cleaning cache " + self.file)
        os.remove(self.file)

    def is_valid(self):
        if os.path.isfile(self.file):
            return True
        else:
            return False
