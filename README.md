# RansomLeakMonitor
This tool is meant to help automate the identification of new victims that are posted to common threat actor leak sites. 

## Requirements
This tool was tested using ubuntu 20.04 server. Other requirements include:
- Phpmyadmin (any version, just for simple db modification)
- MySQL (likely any reasonably up to date version)
- Python3 - I am using Python 3.8


## Installation
- Install MySQL - https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04
  - NOTE: I had issues with MySQL using auth_socket insteald of password. This can be fixed via googling.
- Install phpMyAdmin - https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-phpmyadmin-on-ubuntu-20-04
- Install TOR (```sudo apt-get install tor```)
- Install TOR Bundle (browser package used for screenshots)- https://www.torproject.org/download/
- Install TOR-Browser-Selenium - follow instructions for installing here: https://github.com/webfp/tor-browser-selenium - make sure to copy the gecko driver to ```/usr/bin``` and do not skip xvfb install either!
- Install some missing tools - ```sudo apt install build-essential libdbus-glib-1-dev libgirepository1.0-dev```
- Install some missing dependencies: ```pip3 install pysocks urllib3 requests regex proxies dbus-python```
- Clone this repository
- Run pip3 install -r requirements.txt to satisfy python dependencies
- Import ransomleakmonitor.sql into phpmyadmin to reproduce the database and schema
- Edit config.yaml to include proper webhooks, database info, imagbb api details, and threat actor URLs

## Running RansomLeakMonitor
- python3 allinone.py

## Setting RansomLeakMonitor to run on a schedule
For linux, cron does a great job - run ```crontab -e``` and enter:
```30 * * * * cd <directory of ransomleakmonitor> && python3 allinone.py```
Would run every hour on the :30 minute mark

Note: it can be helpful to run ```export $PATH``` and copy the output to the top of your cron job list to help with site variables
