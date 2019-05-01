#!/bin/bash
NAME=$1
SCORE=$2

camera_script=$(cat "$SETTINGS_FILE" | `which shyaml` get-value "File Location"."Camera Script"."val")

if [[ "$NAME" == "Max" ]]; then
    # play music!
    play /music/welcome.mp3
fi

echo "BASH $NAME"
