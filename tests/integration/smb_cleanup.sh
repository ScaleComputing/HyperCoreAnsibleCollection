#!/bin/bash

${SMB_PASSWORD}
${SMB_USERNAME}
${SMB_SHARE}
${SMB_SERVER}

SC_HOST=$(( $SMB_SERVER | sed 's/http/hTTp/' ))

echo $SC_HOST
echo $(( ${SMB_SERVER} | sed 's/http/hTTp/' ))
echo $(( $SMB_SERVER | sed 's/http/hTTp/' ))

sshpass -p root ssh root@${SMB_SERVER}
echo "BLA"