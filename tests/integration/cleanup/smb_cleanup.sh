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

export_files=($(smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-export' -c ls | awk '{print $1}'))
export_dates=($(smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-export' -c ls -l | awk '{print $5":"$6":"$8}'))
import_files=($(smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-import' -c ls | awk '{print $1}'))
import_dates=($(smbclient //$1$2 -U "administrator"%"Scale2020!" -D 'integration-test-vm-import' -c ls -l | awk '{print $5":"$6":"$8}'))

today_date=$(date +'%b:%d:%Y')
echo "Todays date:" $today_date
echo "export files:" ${export_files[3]}
echo "export dates:" ${export_dates[3]}

exit 0


length=${#export_files[@]}-1
for (( j=0; j<length; j++ ));
do
    # Delete files that are at least one day old, in order to not crash other integration tests
    if [ ${files[j]} != '.' ] && [ ${files[j]} != '..' ] && [ ${files[j]} != '.deleted' ] && [ ${dates[j]} != $today_date ] 
    then
        echo "Attempting to delete:" ${files[j]} "with timestamp:" ${dates[j]}
        smbclient //$SMB_SERVER$SMB_SHARE -U ${username[1]}%$SMB_PASSWORD -c 'deltree '$file''
    fi
done
