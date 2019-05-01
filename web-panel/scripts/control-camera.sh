#!/bin/bash
# Script will either stop, start or restart the python script running the camera.

# get location of camera script run.py
SETTINGS_FILE="/var/www/web-panel/settings.yaml"

if [[ "$1" != "stop" && "$1" != "restart" && "$1" != "start" ]]
then
    echo "invalid or no argument {stop, start, restart}"
    exit
fi

script=$(cat "$SETTINGS_FILE" | `which shyaml` get-value "File Location"."Camera Script"."val")
if [[ "$script" == "" ]]
then
    echo "ERROR: Is this the correct settings file '$SETTINGS_FILE'?<br><br> Is shyaml installed? -> pip install shyaml"
    exit
fi

if [[ "$1" == "stop" || "$1" == "restart" ]]
then
    # kill script
    `which pkill` -f "$script"
    if [ $? != 0 ]; then
        # Process kill failed - silent exit as do not want to potentially
        # start the process up again (restart) if camera wasn't already asked to be on.
        exit
    fi
fi

if [[ "$1" == "start" || "$1" == "restart" ]]
then
    # start script
    `which python` "$script"> /dev/null &
    #TODO: need to debug whether this has worked
fi