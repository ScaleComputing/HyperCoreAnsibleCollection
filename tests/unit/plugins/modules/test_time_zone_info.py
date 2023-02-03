# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    time_zone_info,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRun:
    def test_run_record_present(self, rest_client):
        rest_client.list_records.return_value = [
            dict(
                uuid="test",
                timeZone="US/Eastern",
                latestTaskTag={},
            )
        ]

        result = time_zone_info.run(rest_client)
        assert result == {
            "uuid": "test",
            "time_zone": "US/Eastern",
            "latest_task_tag": {},
        }

    def test_run_record_absent(self, rest_client):
        rest_client.list_records.return_value = []

        result = time_zone_info.run(rest_client)
        assert result == {}
