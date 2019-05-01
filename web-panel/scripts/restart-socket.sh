#!/bin/bash
# kills the python socket script and starts it again to reconnect
#in sudo visudo
#www-data ALL = (root) NOPASSWD: /var/www/web-panel/scripts/*

SETTINGS_FILE="/var/www/web-panel/settings.yaml"

socket_script=$(cat "$SETTINGS_FILE" | `which shyaml` get-value "File Location"."Socket Script"."val")

# kill socket script
ps -ef | grep "$socket_script" | grep -v grep | awk '{print $2}' | xargs kill -9

# start socket script
`which python` "$socket_script"> /dev/null &