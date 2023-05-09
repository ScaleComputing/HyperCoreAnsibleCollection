# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot import (
    VMSnapshot,
)

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_snapshot_info

from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRun:
    def setup_method(self):
        self.params=dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin"
            ),
            vm_name=None,
            serial=None,
            label=None,
        )

    def test_run_present(self, create_module, rest_client):
        module = create_module(
            params=self.params,
        )

        hypercore_dict = dict(
                uuid="test",
                domainUUID="vm-uuid",
                domain={
                    "name": "vm-name",
                    "snapshotSerialNumber": 1,
                    "blockDevs": [
                        {
                            "cacheMode": "WRITETHROUGH",
                            "capacity": 100,
                            "disableSnapshotting": False,
                            "readOnly": False,
                            "slot": 0,
                            "tieringPriorityFactor": 8,
                            "type": "VIRTIO_DISK",
                            "uuid": "block-uuid-1",
                        },
                    ],
                },
                deviceSnapshots=[
                    {
                        "uuid": "block-uuid-1",
                    },
                ],
                timestamp=123,
                label="snapshot",
                type="USER",
                automatedTriggerTimestamp=111,
                localRetainUntilTimestamp=222,
                remoteRetainUntilTimestamp=333,
                blockCountDiffFromSerialNumber=444,
                replication=True,
            )

        rest_client.list_records.return_value = [hypercore_dict]

        expected = dict(
            snapshot_uuid="test",
            vm={
                "name": "vm-name",
                "uuid": "vm-uuid",
                "snapshot_serial_number": 1,
                "block_devices": [
                    {
                        "cache_mode": "WRITETHROUGH",
                        "capacity": 100,
                        "disable_snapshotting": False,
                        "read_only": False,
                        "slot": 0,
                        "tiering_priority_factor": 8,
                        "type": "VIRTIO_DISK",
                        "uuid": "block-uuid-1",
                    },
                ]
            },
            device_snapshots=[
                {
                    "uuid": "block-uuid-1",
                },
            ],
            timestamp=123,
            label="snapshot",
            type="USER",
            automated_trigger_timestamp=111,
            local_retain_until_timestamp=222,
            remote_retain_until_timestamp=333,
            block_count_diff_from_serial_number=444,
            replication=True,
        )

        result = vm_snapshot_info.run(module, rest_client)[0]  # this is safe, since these tests only have one snapshot

        print("RESULT")
        print(result)
        print("\nEXPECTED")
        print(expected)

        result_sorted_block_devices = [
            dict(sorted(bd.items(), key=lambda item: item[0])) for bd in result["vm"]["block_devices"]
        ]
        expected_sorted_block_devices = [
            dict(sorted(bd.items(), key=lambda item: item[0])) for bd in expected["vm"]["block_devices"]
        ]

        assert result["snapshot_uuid"] == expected["snapshot_uuid"]
        assert result["vm"]["name"] == expected["vm"]["name"]
        assert result["vm"]["uuid"] == expected["vm"]["uuid"]
        assert result["vm"]["snapshot_serial_number"] == expected["vm"]["snapshot_serial_number"]
        assert result_sorted_block_devices == expected_sorted_block_devices
        assert result["device_snapshots"] == expected["device_snapshots"]
        assert result["timestamp"] == expected["timestamp"]
        assert result["label"] == expected["label"]
        assert result["type"] == expected["type"]
        assert result["automated_trigger_timestamp"] == expected["automated_trigger_timestamp"]
        assert result["local_retain_until_timestamp"] == expected["local_retain_until_timestamp"]
        assert result["remote_retain_until_timestamp"] == expected["remote_retain_until_timestamp"]
        assert result["block_count_diff_from_serial_number"] == expected["block_count_diff_from_serial_number"]
        assert result["replication"] == expected["replication"]

    def test_run_record_absent(self, create_module, rest_client):
        module = create_module(
            self.params,
        )
        rest_client.list_records.return_value = []

        result = vm_snapshot_info.run(module, rest_client)
        assert result == []
