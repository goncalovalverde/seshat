# Seshat

A tool to extract metrics from agile tools such as Jira.
It is heavilly influenced by the work of Troy Magennis (https://www.focusedobjective.com/) 

Currently the following sources of information are supported:
- Jira
- Trello
- CSV file


## Instalation

Requires Python 3.6 or later.

Install Python 3 and the pip package manager. 

If you're using Windows, install Python from Anaconda distribution (https://www.anaconda.com/products/individual). This will install some essential packages that fail to install via the standard python distribution. No guarantees that it will work well in Windows!

Then run to install required modules:

     $ pip install -r requirements.txt     

## Configuration

Two major configuration files exist, one for configuring logging (log_config.yml) and another for the app main configuration (config.yml)
Also for each project/team a config file needs to be created and stored in the directory configured in config.yml.

Please check conf/ directory with several examples for each case:
- Jira with oauth (server)
- Jira with token (cloud)
- Trello
- Clubhouse.io
- CSV file

### config.yaml
This file provide basic needed information:
config_dir: directory where configuration files for each project are stored
cache_dir: the directory where cache files are stored (needs yet to be implemented)
debug: run application in debug mode or not (applicable for the web interface). Could be set to true or false

### log_config.yml

Change this file to your needs. By default it writes to /tmp/seshat.log

### Project configuration files

Sample files for each type of project have been provided. You can just copy them and rename it to .yml adding your own data

#### Jira
##### Jira passwords

One important note about jira passwords. Jira cloud version no longer support passwords and you need to create an API token instead and then copy&paste it to the password field.
You can find more information about how to create API tokens here:
https://confluence.atlassian.com/cloud/api-tokens-938839638.html

##### oauth

If using oauth authentication (more used for jira server) you will need to create your own certificates for the application and create an application link in you Jira instance. You can find more information about it here:
https://developer.atlassian.com/server/jira/platform/oauth/

To do the oauth dance and get the oauth token you can you can use the python jira-oauth packaget:
https://pypi.org/project/jira-oauth/

Then use this to configure your access following the oauth example in conf/ directory

#### Trello
You need to get a trello API key and secret 
Check here for more information:
https://trello.com/app-key

(in the future oauth support will be provided)

#### Clubhouse.io
You need to get a Clubouse API key

## Usage
### Starting
To run the application just type 

     $python seshat.py 
 
(or just ./seshat.py in unix based OS).

After loading the data and starting with success, use your browser of choice and access http://localhost:80i50/ 


### Running in a server

To run the application in a server and access it from the outside, install a WSGI server (for example gunicorn) and don't forget to bind it to the public address.

For example:

     $ gunicorn --bind 0.0.0.0 seshat:server

## Trivia
### Why Seshat?
I'm not great with names in one hand and in another I would prefer to have something more interesting than "python agile metrics" or similar. So I looked for a name of a god that would make sense and found this in wikipedia:

     Seshat, under various spellings, was the ancient Egyptian goddess of wisdom, knowledge, and writing. 
     She was seen as a scribe and record keeper, and her name means she who scrivens (i.e. she who is the scribe), 
     and is credited with inventing writing.
