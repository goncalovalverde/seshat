#!/usr/bin/python
import yaml
import reader
import calculator.flow
import viewer.team_metrics
import viewer.dash
import logging
import logging.config
import config as cfg

def setup_logging():
    with open("log_config.yaml", "r") as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

def read_data(config):
    projects = []
    for source_config in config["input"]:
        logging.info(f"Reading data for {source_config['name']}")
        data_reader = reader.Reader(source_config)
        team_metrics = viewer.team_metrics.Team_Metrics(data_reader)
        projects.append(team_metrics)
    return projects


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting seshat. Let's do team magic!")

    config = cfg.get()

    projects = read_data(config)

    dash = viewer.dash.Dash(projects, config)

    server = dash.server
    dash.run()

if __name__ == "__main__":
    main()
