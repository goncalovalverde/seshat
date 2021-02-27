from array import ArrayType
import yaml
import glob
import logging


def get(type: str = "all") -> dict:
    with open("config.yml", "r") as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
        if type == "all":
            config["input"] = get_input(config["config_dir"])
            return config

        return config[type]


def get_input(config_dir: str) -> list:
    input = []
    for file_name in sorted(glob.iglob(f"{config_dir}/*.yml")):
        logging.info(f"Reading input configuration from {file_name}")
        with open(file_name, "r") as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
            input.append(config)
    return input


def validate_input_config(config):
    return True
