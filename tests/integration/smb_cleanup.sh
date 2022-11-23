#!/usr/bin/env bash

files=($(smbclient //$SMB_SERVER$SMB_SHARE -U $SMB_USERNAME $SMB_PASSWORD -N -c ls | awk '{print $1}'))
dates=($(smbclient //$SMB_SERVER$SMB_SHARE -U $SMB_USERNAME $SMB_PASSWORD -N -c ls -l | awk '{print $5":"$6":"$8}'))
today_date=$(date +'%b:%d:%Y')

echo "Todays date:" $today_date

length=${#files[@]}-1
for (( j=0; j<length; j++ ));
do
    # Delete files that are at least one day old, in order to not crash other integration tests
    if [ ${files[j]} != '.' ] && [ ${files[j]} != '..' ] && [ ${files[j]} != '.deleted' ] && [ ${dates[j]} != $today_date ] 
    then
        echo "Attempting to delete:" ${files[j]} "with timestamp:" ${dates[j]}
        smbclient //$SMB_SERVER$SMB_SHARE -U $SMB_USERNAME $SMB_PASSWORD -N -c 'deltree '$file''
    fi
done
