# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    email_alert_info,
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
                uuid="8664ed18-c354-4bab-be96-78dae5f6377f",
                alertTagUUID="0",
                emailAddress="test@test.com",
                resendDelay=123,
                silentPeriod=123,
                latestTaskTag={},
            )
        ]

        result = email_alert_info.run(rest_client)
        assert result == [
            {
                "uuid": "8664ed18-c354-4bab-be96-78dae5f6377f",
                "alert_tag_uuid": "0",
                "email_address": "test@test.com",
                "resend_delay": 123,
                "silent_period": 123,
                "latest_task_tag": {},
            }
        ]

    def test_run_record_absent(self, rest_client):
        rest_client.list_records.return_value = []

        result = email_alert_info.run(rest_client)
        assert result == []
