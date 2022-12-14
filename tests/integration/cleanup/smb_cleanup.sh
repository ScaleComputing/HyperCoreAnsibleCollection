#!/usr/bin/env bash

# Delete function.
# Deletes files that are at least one day old.
delete_files () {
    server=$1
    share=$2
    username=$3
    password=$4
    folder=$5 # Folder where files are located.
    files=($(smbclient //$server$share -U $username%$password -D $folder -c ls | awk '{print $1}'))
    dates=($(smbclient //$server$share -U $username%$password -D $folder -c ls -l | awk '{print $5":"$6":"$8}'))
    length=${#files[@]}-1

    # Output list of all files inside given directory, easier to debug.
    echo "Folder:" $folder
    smbclient //$server$share -U $username%$password -D $folder << SMBCLIENTCOMMANDS
    ls
SMBCLIENTCOMMANDS

    today_date=$(date +'%b:%-d:%Y')
    echo "Todays date:" $today_date

    for (( j=0; j<length; j++ ));
    do
        # Delete files that are at least one day old, in order to not crash other integration tests.
        if [ ${files[j]} != '.' ] && [ ${files[j]} != '..' ] && [ ${files[j]} != '.deleted' ] && [ ${dates[j]} != $today_date ] 
        then
            echo "Attempting to delete:" ${files[j]} "with timestamp:" ${dates[j]}
            smbclient //$server$share -U $username%$password -D $folder -c 'deltree '${files[j]}''
        fi
    done
 }

# Main function
main () {
    # $1 server address
    # $2 share on server
    # $3 username
    # $4 password
    # username is provided as domain;username
    IFS=';' read -ra username <<< $3

    folder='integration-test-vm-export'
    delete_files $1 $2 ${username[1]} $4 $folder

    folder='integration-test-vm-import'
    delete_files $1 $2 ${username[1]} $4 $folder

    exit 0
}

main $1 $2 $3 $4
