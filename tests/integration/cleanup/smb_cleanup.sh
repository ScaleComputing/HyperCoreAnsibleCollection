#!/usr/bin/env bash

# USERNAME is provided as domain;username
# server = $1
# share = $2
# username = $3
# password = $4

IFS=';'
read -a username <<< "$3"

smbclient //192.168.1.248/ansibleci -U pm-edge/administrator%Scale2020! -W pm-edge << SMBCLIENTCOMMANDS
ls
SMBCLIENTCOMMANDS

smbclient //$1$2 -U pm-edge/administrator%Scale2020! -W pm-edge << SMBCLIENTCOMMANDS
ls
SMBCLIENTCOMMANDS

echo $username

exit

files=($(smbclient //$SMB_SERVER$SMB_SHARE -U ${username[0]}%$SMB_PASSWORD -c ls | awk '{print $1}'))
dates=($(smbclient //$SMB_SERVER$SMB_SHARE -U ${username[1]}%$SMB_PASSWORD -c ls -l | awk '{print $5":"$6":"$8}'))
today_date=$(date +'%b:%d:%Y')

echo "Todays date:" $today_date

length=${#files[@]}-1
for (( j=0; j<length; j++ ));
do
    # Delete files that are at least one day old, in order to not crash other integration tests
    if [ ${files[j]} != '.' ] && [ ${files[j]} != '..' ] && [ ${files[j]} != '.deleted' ] && [ ${dates[j]} != $today_date ] 
    then
        echo "Attempting to delete:" ${files[j]} "with timestamp:" ${dates[j]}
        smbclient //$SMB_SERVER$SMB_SHARE -U ${username[1]}%$SMB_PASSWORD -c 'deltree '$file''
    fi
done
