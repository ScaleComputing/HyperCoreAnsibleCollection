#!/usr/bin/env bash
set -e  # exit on error
set -u  # exit on undefined variable
# set -x  # verbose

# Delete function.
# Deletes files that are at least one day old.
delete_files () {
    server=$1
    share=$2
    username=$3
    password=$4
    folder=$5 # Folder where files are located.
    # files=($(smbclient //$server$share -U $username%$password -D $folder -c ls | awk '{print $1}'))
    # dates=($(smbclient //$server$share -U $username%$password -D $folder -c ls -l | awk '{print $5":"$6":"$8}'))
    # length=${#files[@]}-1

    list_dir=$(smbclient "//$server$share" -U "$username%$password" -D "$folder" -c l)
    # for each file we have a line is like "  Cuba                                N     2416  Mon Apr 27 10:52:07 2020"
    # Output list of all files inside given directory, easier to debug.
    echo "Folder: $folder"
    echo "list_dir=$list_dir"
    # remove first 2 and last 2 lines of smbclient output - they are not files
    files="$(echo "$list_dir" | head --lines=-2 | tail --lines=+3)"
    echo "files=$files"

    today_date=$(date +'%b:%-d:%Y')
    echo "Todays date: $today_date"

    while IFS= read -r line
    do
      # echo line=$line
      if [ "$line" == "" ]
      then
        # directory is empty
        continue
      fi
      filename="$(echo "$line" | awk '{print $1}')"
      file_date=$(echo "$line" | awk '{print $5":"$6":"$8}')
      if [ $file_date == $today_date ]
      then
        echo "Keeping file $filename, timestamp is $file_date"
        continue
      fi
      echo "Removing file $filename, timestamp is $file_date"
      smbclient "//$server$share" -U "$username%$password" -D "$folder" -c "deltree $filename"
    done <<< "$files"
}

# Main function
main () {
    # $1 server address
    # $2 share on server
    # $3 username
    # $4 password
    # username is provided as domain;username
    IFS=';' read -ra username <<< "$3"

    folder='integration-test-vm-export'
    delete_files "$1" "$2" "${username[1]}" "$4" "$folder"

    folder='integration-test-vm-import'
    delete_files "$1" "$2" "${username[1]}" "$4" "$folder"

    exit 0
}

main "$1" "$2" "$3" "$4"
