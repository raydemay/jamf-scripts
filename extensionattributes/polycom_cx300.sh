#!/usr/bin/env sh

# Checks to see if a Polycom CX300 phone is connected

if system_profiler SPUSBDataType | grep -q "Polycom CX300"; then 
    result="True"
else
    result="False"
fi

echo "<result>$result</result>"
