# Seshat

A tool to extract metrics from agile tools such as Jira (currently only supporting Jira and CSV)

## Instalation

Requires Python 3.6 or later.

Install Python 3 and the pip package manager. Then run to install required modules:

     $ pip install -r requirements.txt
     
## Configuration

Two configuration files exist, one for configuring logging (log_config.yaml) and another for the app configuration (config.yaml)

### Config.yaml
An example file is provided called config.yaml-example.

Copy this file to config.yaml and change it to your needs.

#### Jira passwords

One important note about jira passwords. Jira cloud version no longer support passwords and you need to create an API token instead and then copy&paste it to the password field.
You can find more information about how to create API tokens here:
https://confluence.atlassian.com/cloud/api-tokens-938839638.html

## Usage
### Starting
To run the application just type ./seshat.py and after starting access http://localhost:8050/ using your browser of choice
