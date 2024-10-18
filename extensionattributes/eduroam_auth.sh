#!/bin/zsh
###########################################################################################
# Extension Attribute to check if 802.1X is doing user auth or using the device certificate
# Author: Ray DeMay
# Created: 2024-10-17
###########################################################################################

account=$(security find-generic-password -D "802.1X Password" -s "com.apple.network.eap.system.item.wlan.ssid.eduroam" | grep acct | sed 's/.*=//' | tr -d '"')
eduroam_cert=$(security find-identity -v /Library/Keychains/System.keychain | awk '{print $3}' | tr -d '"' | grep @jamf.it.osu.edu)

if [[ $account == $eduroam_cert ]]; then
    echo "<result>Device Certificate</result>"
else
    echo "<result>User Authentication</result>"
fi
