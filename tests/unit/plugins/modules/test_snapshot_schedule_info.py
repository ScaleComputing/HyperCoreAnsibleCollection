# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    snapshot_schedule_info,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRun:
    def test_run_records_present(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="snapshot-schedule-image-name",
            ),
        )

        rest_client.list_records.return_value = [
            dict(
                name="snapshot-name",
                uuid="id",
                rrules=[
                    dict(
                        name="recurrence-name",
                        rrule="FREQ=WEEKLY",
                        dtstart="2010-01-01 00:00:00",
                        localRetentionDurationSeconds=6048000,
                        remoteRetentionDurationSeconds=6048000,
                        replication=True,
                        uuid="id",
                    )
                ],
            )
        ]

        result = snapshot_schedule_info.run(module, rest_client)
        assert result == [
            dict(
                name="snapshot-name",
                uuid="id",
                recurrences=[
                    dict(
                        name="recurrence-name",
                        frequency="FREQ=WEEKLY",
                        start="2010-01-01 00:00:00",
                        local_retention=6048000,
                        remote_retention=6048000,
                        replication=True,
                        uuid="id",
                    )
                ],
            )
        ]

    def test_run_records_absent(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="snapshot-schedule-image-name",
            ),
        )

        rest_client.list_records.return_value = []

        result = snapshot_schedule_info.run(module, rest_client)
        assert result == []
