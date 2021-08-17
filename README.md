# RansomLeakMonitor
This tool is meant to help automate the identification of new victims that are posted to common threat actor leak sites. 

## Features
- Scan 20 leak sites for new victims and alert via Discord or Teams
- Store images of the leak site and  victims in MySQL database for retention
- Easily add additional parsers as new sites come online

## Requirements
This tool was tested using ubuntu 20.04 server. Other requirements include:
- Phpmyadmin (any version, just for simple db modification)
- MySQL (likely any reasonably up to date version)
- Python3 - I am using Python 3.8 and pip3 (```sudo apt-get install python3-pip```)


## Installation
- Install some missing tools - ```sudo apt install build-essential git libdbus-glib-1-dev libgirepository1.0-dev```
- Install MySQL - https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04
  - NOTE: MySQL doesn't like root logons anymore- create a user with good privs - https://devanswers.co/phpmyadmin-access-denied-for-user-root-localhost/
- Install phpMyAdmin - https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-phpmyadmin-on-ubuntu-20-04
- Install TOR (```sudo apt-get install tor```)
- Install TOR Bundle (browser package used for screenshots)- https://www.torproject.org/download/
- Install TOR-Browser-Selenium - follow instructions for installing here: https://github.com/webfp/tor-browser-selenium - make sure to copy the gecko driver to ```/usr/bin``` and do not skip xvfb install either!
- Install some missing dependencies: ```pip3 install pysocks urllib3 requests regex proxies dbus-python```
- Clone this repository
- Run pip3 install -r requirements.txt to satisfy python dependencies
- Import ransomleakmonitor.sql into phpmyadmin to reproduce the database and schema
- Edit config.yaml to include proper webhooks, database info, imagbb api details, and threat actor URLs

## Running RansomLeakMonitor
```python3 allinone.py```

## Setting RansomLeakMonitor to run on a schedule
For linux, cron does a great job - run ```crontab -e``` and enter:
```30 * * * * cd <directory of ransomleakmonitor> && python3 allinone.py```
Would run every hour on the :30 minute mark

Note: it can be helpful to run ```export $PATH``` and copy the output to the top of your cron job list to help with site variables
