#!/bin/bash
# added to /etc/rc.local

SETTINGS_FILE="/var/www/web-panel/settings.yaml"
chown www-data:www-data -R /var/www/web-panel/images/

# start script process' in bg

camera_script=$(cat "$SETTINGS_FILE" | `which shyaml` get-value "File Location"."Camera Script"."val")
socket_script=$(cat "$SETTINGS_FILE" | `which shyaml` get-value "File Location"."Camera Script"."val")

`which python` "$camera_script" &
`which python` "$socket_script" &

#until `which python` "$camera_script"; do
#    #todo send to DB log that script crashed
#    sleep 5 # sleep for 5 secs until run again
#done