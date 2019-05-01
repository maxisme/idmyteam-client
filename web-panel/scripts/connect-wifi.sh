#!/bin/bash
# script used to connect to wifi hot-spot
name=$1
pass=$2

# check if there is a network with $name
if ! iwlist scan | grep "\"$name\"" &> /dev/null
then
   echo "No such SSID - '$name'";
   exit
fi

# terminate access point to allow for wifi connection attempt
service hostapd stop
service dnsmasq stop

echo -e "
network={
        ssid=\"$name\"
        psk=\"$pass\"
}
" >> /etc/wpa_supplicant/wpa_supplicant.conf

sed -i '/## AP ##/,/##--##/d' /etc/network/interfaces

echo -e "
iface wlan0 inet manual
wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
" >> /etc/network/interfaces

service networking restart
