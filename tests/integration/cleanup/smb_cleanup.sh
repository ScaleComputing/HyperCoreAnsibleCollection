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
    smbclient //$1$2 -U $3%$4 -D $7 << SMBCLIENTCOMMANDS
    ls
SMBCLIENTCOMMANDS

    today_date=$(date +'%b:%d:%Y')
    echo "Todays date:" $today_date
    set $5[*]
    ref=(${!5})
    length=${ref[*]}
    echo "length:" $length
    echo "whatever:" $5
    for (( j=0; j<length; j++ ));
    do
        # Delete files that are at least one day old, in order to not crash other integration tests
        if [ ${$5[j]} != '.' ] && [ ${$5[j]} != '..' ] && [ ${$5[j]} != '.deleted' ] && [ ${$6[j]} != $today_date ] 
        then
            echo "Attempting to delete:" ${$5[j]} "with timestamp:" ${$6[j]}
            smbclient //$1$2 -U $3%$4 -D $7 -c 'deltree '${$5[j]}''
        fi
done
 }

echo "Getting variables for export"
folder='integration-test-vm-export'
files=($(smbclient //$1$2 -U ${username[1]}%$4 -D $folder -c ls | awk '{print $1}'))
dates=($(smbclient //$1$2 -U ${username[1]}%$4 -D $folder -c ls -l | awk '{print $5":"$6":"$8}'))
echo "first function call"
delete_files $1 $2 ${username[1]} $4 $files $dates $folder

folder='integration-test-vm-import'
files=($(smbclient //$1$2 -U ${username[1]}%$4 -D $folder -c ls | awk '{print $1}'))
dates=($(smbclient //$1$2 -U ${username[1]}%$4 -D $folder -c ls -l | awk '{print $5":"$6":"$8}'))

delete_files $1 $2 ${username[1]} $4 $files $dates $folder
