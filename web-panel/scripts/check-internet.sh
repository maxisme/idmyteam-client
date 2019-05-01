#!/bin/bash

if ! ping -c 2 8.8.8.8 &> /dev/null
then

#    service hostapd start
#    service dnsmasq start
else
    # stop access point as not needed if connected to internet
#    service hostapd stop
#    service dnsmasq stop
    curl -d "credentials=SFE82Li5zEzI1Z99ot42nUUeM" \
-d "title=Lorem ipsum dolor." \
-d "message=Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." \
-d "link=https://notifi.it" \
-d "image=https://notifi.it/images/logo.png" \
https://notifi.it/api
fi

