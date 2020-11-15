import yaml
import os


def get():
    with open("config.yml", "r") as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
        # Add special "issue_type" Total to ensure we can see the total in all graphs
        config["issue_type"].insert(0, "Total")
    return config


def read_input_files():
    config_files = os.listdir("conf/")
    return config_files


def validate_input_config(config):
    return True
