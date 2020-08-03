#!/usr/bin/python
import yaml

config_file=open("config.yml")
config=yaml.load(config_file,Loader=yaml.FullLoader)

print(config["jira"]["username"])