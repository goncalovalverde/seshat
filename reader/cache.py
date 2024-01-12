import pandas as pd
import logging
from pathlib import Path
import config

class Cache:
    def __init__(self, filename: str):
        """Initializes the Cache with a specified filename."""
        cache_dir = config.get("cache_dir")
        self.file = Path(cache_dir) / f"seshat_cache_{filename}.pkl"
        logging.info("Initializing Cache")

    def write(self, data: pd.DataFrame) -> None:
        """Writes the provided data to the cache."""
        logging.debug("Writing to cache %s", self.file)
        data.to_pickle(self.file)

    def read(self) -> pd.DataFrame:
        """Reads data from the cache and returns it."""
        if not self.file.exists():
            raise FileNotFoundError(f"No cache file found at {self.file}")
        logging.debug("Reading from cache %s", self.file)
        data = pd.read_pickle(self.file)
        return data

    def clean(self) -> None:
        """Removes the cache file."""
        if not self.file.exists():
            raise FileNotFoundError(f"No cache file found at {self.file}")
        logging.debug("Cleaning cache %s", self.file)
        self.file.unlink()

    def is_valid(self) -> bool:
        """Checks if the cache file exists and returns True if it does, False otherwise."""
        return self.file.exists()