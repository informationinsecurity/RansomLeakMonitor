#!/bin/bash
#make-run.sh
#make sure a process is always running.

process="listener.py"
makerun="/home/ubuntu/RansomLeakMonitor/db_listener/listener.py"

if ps ax | grep -v grep | grep $process > /dev/null
then
    echo "process running!"
    exit
else
    python3 $makerun &
fi

exit
