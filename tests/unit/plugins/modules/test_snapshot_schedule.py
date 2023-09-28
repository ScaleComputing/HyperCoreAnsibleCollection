# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    snapshot_schedule,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestEnsureAbsent:
    def test_ensure_absent(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="SnapshotSchedule-image-name",
                state="absent",
            ),
        )

        rest_client.get_record.return_value = dict(
            uuid="id",
            name="SnapshotSchedule-test-name",
            rrules=[],
        )
        rest_client.delete_record.return_value = dict(taskTag="", createdUUID="")
        result = snapshot_schedule.ensure_absent(module, rest_client)
        assert result == (
            True,
            [{"name": "SnapshotSchedule-test-name", "recurrences": [], "uuid": "id"}],
            {
                "after": None,
                "before": {
                    "name": "SnapshotSchedule-test-name",
                    "recurrences": [],
                    "uuid": "id",
                },
            },
        )


class TestEnsurePresent:
    def test_ensure_present_snapshot_schedule_record_present_no_update(
        self, create_module, rest_client
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="SnapshotSchedule-image-name",
                state="present",
                source="/path/to/source",
                recurrences=[],
            ),
        )

        rest_client.get_record.return_value = dict(
            uuid="id",
            name="SnapshotSchedule-test-name",
            rrules=[],
        )

        rest_client.update_record.return_value = None
        result = snapshot_schedule.ensure_present(module, rest_client)

        rest_client.create_record.assert_not_called()
        rest_client.update_record.assert_not_called()

        assert result == (
            False,
            [{"name": "SnapshotSchedule-test-name", "recurrences": [], "uuid": "id"}],
            {
                "after": {
                    "name": "SnapshotSchedule-test-name",
                    "recurrences": [],
                    "uuid": "id",
                },
                "before": {
                    "name": "SnapshotSchedule-test-name",
                    "recurrences": [],
                    "uuid": "id",
                },
            },
        )

    def test_ensure_present_snapshot_schedule_record_updated(
        self, create_module, rest_client
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="SnapshotSchedule-image-name",
                state="present",
                source="/path/to/source",
                recurrences=[
                    dict(
                        name="weekly - tuesday",
                        frequency="FREQ=WEEKLY;INTERVAL=1;BYDAY=TU",
                        start="2010-01-01 00:00:00",
                        local_retention=604800,
                        remote_retention=None,
                    )
                ],
            ),
        )

        rest_client.get_record.return_value = dict(
            uuid="id",
            name="SnapshotSchedule-test-name",
            rrules=[],
        )

        rest_client.update_record.return_value = None
        result = snapshot_schedule.ensure_present(module, rest_client)

        rest_client.create_record.assert_not_called()
        rest_client.update_record.assert_called_once()

        assert result == (
            True,
            [{"name": "SnapshotSchedule-test-name", "recurrences": [], "uuid": "id"}],
            {
                "after": {
                    "name": "SnapshotSchedule-test-name",
                    "recurrences": [],
                    "uuid": "id",
                },
                "before": {
                    "name": "SnapshotSchedule-test-name",
                    "recurrences": [],
                    "uuid": "id",
                },
            },
        )

    def test_ensure_present_snapshot_schedule_image_absent(
        self, create_module, rest_client
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="SnapshotSchedule-image-name",
                source="/path/to/source",
                state="present",
            ),
        )
        rest_client.get_record.side_effect = [
            None,
            dict(
                uuid="id",
                name="SnapshotSchedule-test-name",
                rrules=[],
            ),
        ]
        rest_client.create_record.return_value = None
        result = snapshot_schedule.ensure_present(module, rest_client)
        assert result == (
            True,
            [{"name": "SnapshotSchedule-test-name", "recurrences": [], "uuid": "id"}],
            {
                "after": {
                    "name": "SnapshotSchedule-test-name",
                    "recurrences": [],
                    "uuid": "id",
                },
                "before": None,
            },
        )
