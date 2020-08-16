#!/usr/bin/python
import yaml
import pandas as pd
import reader.jira
import reader.csv
import calculator.flow
import viewer.team_metrics

config_file = open("config.yml")
config = yaml.load(config_file, Loader=yaml.FullLoader)
mode = config["input"]["mode"]


if mode == "csv":
    cycle_data = reader.csv.read_csv(
        config["input"]["csv_file"], config["Workflow"])
elif mode == "jira":
    jira = reader.jira.Jira(config["jira"],config["Workflow"])
    cycle_data = pd.DataFrame(jira.get_jira_data())

print(cycle_data)

if config["output"]["format"] == "xslx":
    with pd.ExcelWriter(config["output"]["filename"]) as writer:
        cycle_data.to_excel(writer)

#throughput = calculator.flow.throughput(cycle_data)
# throughput = calculator.flow.defect_percentage(throughput)
#print(throughput)
# viewer.team_metrics.show_defect_percentage(throughput)
# print(throughput)
net_flow=calculator.flow.net_flow(cycle_data)
viewer.team_metrics.show_net_flow(net_flow)
# calculator.flow.lead_time(cycle_data)
# viewer.team_metrics.show_lead_time(cycle_data)

# viewer.team_metrics.show_throughput(throughput)
