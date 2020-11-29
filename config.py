import yaml
import glob
import logging


def get():
    with open("config.yml", "r") as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
        # Add special "issue_type" Total to ensure we can see the total in all graphs
        config["input"] = get_input(config["config_dir"])
    return config


def get_input(config_dir):
    input = []
    for file_name in glob.iglob(f"{config_dir}/*.yml"):
        logging.error(f"Reading input configuration from {file_name}")
        with open(file_name, "r") as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
            config["issue_types"].insert(0, "Total")
            input.append(config)
    return input


def validate_input_config(config):
    return True
