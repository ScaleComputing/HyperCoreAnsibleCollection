#!/usr/bin/env python

# The script needs to provide output compatible with
# https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-environment-variable

# Test as:
# cat .github/sample_data_sc_all.yml | SC_VERSION=9.1 python .github/load_sc_secrets.py > ci_new_env.sh
# source ci_new_env.sh
# echo SC_HOST=$SC_HOST

import yaml
import sys
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    data_all = yaml.safe_load(sys.stdin)
    logger.debug(f"data_all={data_all}")
    sc_version = os.environ["SC_VERSION"]
    logger.debug(f"sc_version={sc_version}")
    data = data_all["SC_ALL"][sc_version]
    logger.debug(f"data={data}")

    print(f"# environ variables for SC_VERSION={sc_version}")
    for kk in data:
        print(f"{kk}=\"{data[kk]}\"")


if __name__ == "__main__":
    main()
