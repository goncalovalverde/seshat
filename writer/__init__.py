import pandas as pd
import logging

def write(data,config):
    if config["format"] == "xlsx":
        logging.debug("Writing cycle_data to excel file " + config["filename"])
        with pd.ExcelWriter(config["filename"]) as writer:
            data.to_excel(config["filename"])
    elif config["format"] == "csv":
        logging.debug("Writing cycle_data to csv file " + config["filename"])
        data.to_csv(config["filename"],index=False)
    else:
        logging.debug("I don't have a clue of what I should be doing")