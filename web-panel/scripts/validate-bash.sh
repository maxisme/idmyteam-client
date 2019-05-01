#!/bin/bash
#apt-get install shellcheck
echo "$(cat "$1" | tr -d '\r')"> "$1" # filter php input new lines '\r'
`which shellcheck` "$1"