#!/bin/bash
# runs the python upload script at the specified "Recurring Time".
SETTINGS_FILE="/var/www/web-panel/settings.yaml"

if [[ "$1" != "" ]] # CHECK IF FROM CRON
then
    # upload new classifications from cron job at specified time
    recurring_time=$(cat "$SETTINGS_FILE" | `which shyaml` get-value "Training"."Recurring Time"."val")
    now=$(date +%H:%M)
    if [[ "$now" != "$recurring_time" ]]
    then
        exit
    fi
fi

upload_script=$(cat "$SETTINGS_FILE" | `which shyaml` get-value "File Location"."Train Script"."val")

`which python` "$upload_script"> /dev/null &