#!/usr/bin/env bash

# server = $1
# share = $2
# username = $3
# password = $4

# username is provided as domain;username
# IFS=';' read -ra username <<< "$3"


smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-export' << SMBCLIENTCOMMANDS
ls
SMBCLIENTCOMMANDS

smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-import' << SMBCLIENTCOMMANDS
ls
SMBCLIENTCOMMANDS

export_files=($(smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-export' -c ls | awk '{print $1}'))
export_dates=($(smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-export' -c ls -l | awk '{print $5":"$6":"$8}'))
import_files=($(smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-import' -c ls | awk '{print $1}'))
import_dates=($(smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-import' -c ls -l | awk '{print $5":"$6":"$8}'))

today_date=$(date +'%b:%d:%Y')
echo "Todays date:" $today_date

length=${#export_files[@]}-1
for (( j=0; j<length; j++ ));
do
    # Delete files that are at least one day old, in order to not crash other integration tests
    if [ ${export_files[j]} != '.' ] && [ ${export_files[j]} != '..' ] && [ ${export_files[j]} != '.deleted' ] && [ ${export_dates[j]} != $today_date ] 
    then
        echo "Attempting to delete:" ${export_files[j]} "with timestamp:" ${export_dates[j]}
        smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-export' -c 'deltree '${export_files[j]}''
    fi
done

length=${#import_files[@]}-1
for (( j=0; j<length; j++ ));
do
    if [ ${import_files[j]} != '.' ] && [ ${import_files[j]} != '..' ] && [ ${import_files[j]} != '.deleted' ] && [ ${import_dates[j]} != $today_date ] 
    then
        echo "Attempting to delete:" ${import_files[j]} "with timestamp:" ${import_dates[j]}
        smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-import' -c 'deltree '${import_files[j]}''
    fi
done
