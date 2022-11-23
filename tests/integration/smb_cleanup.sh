#!/bin/bash

files=($(smbclient //$SMB_SERVER$SMB_SHARE -U $SMB_USERNAME $SMB_PASSWORD -N -c ls | awk '{print $1}'))
#dates=($(smbclient //$SMB_SERVER$SMB_SHARE -U $SMB_USERNAME $SMB_PASSWORD -N -c ls -l | awk '{print $4}'))

echo "BLA"

for file in ${files[@]}
do
    if [ $file != '.' ] && [ $file != '..' ]
    then
        echo "Attempting to delete:" $file
        smbclient //$SMB_SERVER$SMB_SHARE -U $SMB_USERNAME $SMB_PASSWORD -N -c 'deltree '$file''
    fi
done
