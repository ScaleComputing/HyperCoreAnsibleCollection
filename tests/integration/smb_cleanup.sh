#!/bin/bash

${SMB_PASSWORD}
${SMB_USERNAME}
${SMB_SHARE}
${SMB_SERVER}


sshpass -p root ssh root@${SMB_SERVER}
echo "BLA"