# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    dns_config_info,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRun:
    def test_run_record_present(self, rest_client):
        rest_client.list_records.return_value = [
            dict(
                uuid="test",
                searchDomains=["example.domain1.com", "example.domain2.com"],
                serverIPs=["1.2.3.4", "5.6.7.8"],
                latestTaskTag={},
            )
        ]

        result = dns_config_info.run(rest_client)
        assert result == {
            "uuid": "test",
            "search_domains": ["example.domain1.com", "example.domain2.com"],
            "server_ips": ["1.2.3.4", "5.6.7.8"],
            "latest_task_tag": {},
        }

    def test_run_record_absent(self, rest_client):
        rest_client.list_records.return_value = []

        result = dns_config_info.run(rest_client)
        assert result == {}
