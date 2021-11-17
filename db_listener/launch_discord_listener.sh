#!/bin/bash
#make-run.sh
#make sure a process is always running.

process="discord_listener.py"
makerun="/home/ubuntu/RansomLeakMonitor/db_listener/discord_listener.py"

if ps ax | grep -v grep | grep $process > /dev/null
then
    echo "killing old process"
    ps -ef | grep discord_listener.py | grep -v grep | awk '{print $2}' | xargs kill
    python3 $makerun &
    exit
else
    python3 $makerun &
fi

exit
