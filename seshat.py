#!/usr/bin/python
from numpy.core.fromnumeric import cumprod
import yaml
import reader
import calculator.flow
import viewer.team_metrics
import viewer.dash
import logging
import logging.config
import writer

with open('log_config.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)
logger.info("Starting seshat. Let's do team magic!")

with open("config.yml", 'r') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
# Add special "issue_type" Total to ensure we can see the total in all graphs
    config["issue_type"].insert(0, "Total")

cycle_data = reader.read_data(config)

throughput = calculator.flow.throughput(cycle_data)

print(calculator.flow.velocity(cycle_data))

# get the first element of the workflow
# to know where to start calculating the lead time
workflow_keys = list(config["Workflow"].keys())
start = workflow_keys[0]
start = "Created"

# adding lead time to cycle_data
cycle_data = calculator.flow.lead_time(cycle_data, start)

# adding cycle_time (between workflow steps) to cycle_data
for i in range(len(workflow_keys)-1):
    start = workflow_keys[i]
    end = workflow_keys[i+1]
    # adding cycle_time to cycle_data
    calculator.flow.cycle_time(cycle_data, start, end)

team_metrics = viewer.team_metrics.Team_Metrics(cycle_data, throughput, config)
dash = viewer.dash.Dash(team_metrics, config)

if config["output"]:
    writer.write_data(cycle_data, config["output"])

server = dash.server

if __name__ == '__main__':
    dash.run()
