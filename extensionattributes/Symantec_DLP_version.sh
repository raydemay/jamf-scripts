#!/bin/sh

if [[ -e "/Library/Manufacturer/Endpoint Agent/Symantec.app/Contents/Info.plist" ]]; then
    version=$(defaults read /Library/Manufacturer/Endpoint\ Agent/Symantec.app/Contents/Info.plist CFBundleShortVersionString)
    echo "<result>$version</result>"
else
    echo "<result>Not Installed</result>"
fi
