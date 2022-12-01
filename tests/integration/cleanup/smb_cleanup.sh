#!/usr/bin/env bash

# server = $1
# share = $2
# username = $3
# password = $4

# username is provided as domain;username
# IFS=';' read -ra username <<< "$3"


smbclient //$1$2 -U "administrator"%"Scale2020!" << SMBCLIENTCOMMANDS
ls
SMBCLIENTCOMMANDS

exit 0


