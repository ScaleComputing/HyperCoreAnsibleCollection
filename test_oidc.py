#!/usr/bin/env python3


import logging
import requests
import time
import copy
import sys

_level = logging.DEBUG
_level = logging.INFO
_format = '%(asctime)s %(name)s %(message)s'
logging.basicConfig(
    level=_level,
    format=_format,
#    datefmt="%Y-%m-%dT%H:%M:%S.%u%z",
)
logger = logging.getLogger(__name__)

API_URL="https://172.31.6.11/rest/v1"
auth = ("admin", "admin")

import urllib3
urllib3.disable_warnings()


def monitor():
    cnt = 0
    logger.warning(f"Start monitor")
    session = requests.Session()
    while 1:
        response = session.get(API_URL + "/ping", auth=auth, verify=False)
        logger.debug(f"cnt={cnt} response status={response.status_code} content={response.content[:100]}")
        if response.status_code != 200:
            logger.warning(f"cnt={cnt} response status={response.status_code} content={response.content}")
        cnt += 1
        time.sleep(0.001)


def oidc():
    logger.warning(f"Start OIDC")
    url = API_URL + "/OIDCConfig"
    response = requests.get(url, auth=auth, verify=False)
    logger.info(f"OIDC GET status={response.status_code} content={response.content}")
    
    payload_a = dict(
        clientID="d2298ec0-0596-49d2-9554-840a2fe20603",
        sharedSecret="~0lI5n-_8dNbWmrrqqTE1v1iBcfO4__jfx",
        configurationURL="https://login.microsoftonline.com/76d4c62a-a9ca-4dc2-9187-e2cc4d9abe7f/v2.0/.well-known/openid-configuration",
        scopes="openid+profile",
    )
    payload_b = copy.copy(payload_a)
    payload_b["clientID"]="12345b-" + str(time.time())
    url = API_URL + "/OIDCConfig/oidcconfig_uuid"

    response = requests.post(url, auth=auth, verify=False, json=payload_a)
    logger.info(f"OIDC a POST status={response.status_code} content={response.content}")
    time.sleep(3)
    response = requests.post(url, auth=auth, verify=False, json=payload_b)
    logger.info(f"OIDC b POST status={response.status_code} content={response.content}")


def main():
    mode = sys.argv[1]
    if mode == "0":
        monitor()
    else:
        oidc()


main()
