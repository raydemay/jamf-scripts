#!/bin/zsh

bat_pct=$(/usr/libexec/PlistBuddy -c 'Print "Maximum Capacity Percent"' /dev/stdin <<< $(pmset -g ps -xml) 2>/dev/null)

if [[ -n $bat_pct ]]; then
	echo "<result>$bat_pct</result>"
else
	echo "<result>No Data</result>"
fi
