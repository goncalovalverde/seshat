#!/usr/bin/python
import yaml
import reader
import calculator.flow
import viewer.team_metrics
import viewer.dash
import logging
import logging.config
import writer
import config

with open("log_config.yaml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)
logger.info("Starting seshat. Let's do team magic!")

config = config.get()

projects = []
for source_config in config["input"]:
    data = reader.read_data(source_config)
    cycle_data = calculator.flow.cycle_data(data, source_config)
    team_metrics = viewer.team_metrics.Team_Metrics(cycle_data, source_config)
    projects.append(team_metrics)

dash = viewer.dash.Dash(projects, config)

server = dash.server

if __name__ == "__main__":
    dash.run()
