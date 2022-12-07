#!/usr/bin/env bash

# server = $1
# share = $2
# username = $3
# password = $4

# username is provided as domain;username
IFS=';' read -ra username <<< $3
echo ${username[0]} ":" ${username[1]}

# Delete function
# server = $1
# share = $2
# username = $3
# password = $4
# files = $5
# dates = $6
# folder = $7
delete_files () { 
    if [ $7 == 'export' ]
    then
        folder='integration-test-vm-export'
    else
        folder='integration-test-vm-import'
    fi
    smbclient //$1$2 -U $3%$4 -D $folder << SMBCLIENTCOMMANDS
    ls
SMBCLIENTCOMMANDS

    today_date=$(date +'%b:%d:%Y')
    echo "Todays date:" $today_date
    length=${#5[@]}-1
    for (( j=0; j<length; j++ ));
    do
        # Delete files that are at least one day old, in order to not crash other integration tests
        if [ ${5[j]} != '.' ] && [ ${5[j]} != '..' ] && [ ${5[j]} != '.deleted' ] && [ ${6[j]} != $today_date ] 
        then
            echo "Attempting to delete:" ${5[j]} "with timestamp:" ${6[j]}
            smbclient //$1$2 -U $3%$4 -D $folder -c 'deltree '${5[j]}''
        fi
done
 }


files=($(smbclient //$1$2 -U ${username[1]}%$4 -D 'integration-test-vm-export' -c ls | awk '{print $1}'))
dates=($(smbclient //$1$2 -U ${username[1]}%$4 -D 'integration-test-vm-export' -c ls -l | awk '{print $5":"$6":"$8}'))

delete_files $1 $2 $username $4 $files $dates 'export'

files=($(smbclient //$1$2 -U ${username[1]}%$4 -D 'integration-test-vm-import' -c ls | awk '{print $1}'))
dates=($(smbclient //$1$2 -U ${username[1]}%$4 -D 'integration-test-vm-import' -c ls -l | awk '{print $5":"$6":"$8}'))

delete_files $1 $2 $username $4 $files $dates 'import'
