# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    smtp_info,
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
                smtpServer="smtp-relay.gmail.com",
                port=25,
                useSSL=True,
                useAuth=True,
                authUser="test",
                # API does not return real password "test123", but only ""
                authPassword="",
                fromAddress="test@test.com",
                latestTaskTag={},
            )
        ]

        result = smtp_info.run(rest_client)
        assert result == {
            "uuid": "test",
            "smtp_server": "smtp-relay.gmail.com",
            "port": 25,
            "use_ssl": True,
            "use_auth": True,
            "auth_user": "test",
            "auth_password": "",
            "from_address": "test@test.com",
            "latest_task_tag": {},
        }

    def test_run_record_absent(self, rest_client):
        rest_client.list_records.return_value = []

        result = smtp_info.run(rest_client)
        assert result == {}
