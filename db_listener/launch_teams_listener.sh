#!/bin/bash
#make-run.sh
#make sure a process is always running.

process="teams_listener.py"

makerun="/home/ubuntu/RansomLeakMonitor/db_listener/teams_listener.py"

if ps ax | grep -v grep | grep $process > /dev/null
then
    echo "killing old process"
    ps -ef | grep teams_listener.py | grep -v grep | awk '{print $2}' | xargs kill
    python3 $makerun &
    echo "process running!"
    exit
else
    python3 $makerun &
fi

exit
