# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
import datetime
from datetime import date

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot import (
    VMSnapshot,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


# Test calculate_data() static method.
class TestCalculateDate:
    @pytest.mark.parametrize(
        "days, expected_output",
        [
            (1, (datetime.datetime.today().date() + datetime.timedelta(days=1))),
            (0, None),
            (None, None),
        ],
    )
    def test_calculate_date(self, days, expected_output):
        result = VMSnapshot.calculate_date(days)
        if result:  # If not None or 0 convert to date.
            result = date.fromtimestamp(result)
        assert result == expected_output


class TestVMSnapshot:
    def setup_method(self):
        self.vm = {
            "name": "test-vm",
            "uuid": "vm-uuid",
            "snapshot_serial_number": 1,
            "disks": [
                {
                    "cache_mode": "writethrough",
                    "size": 100,
                    "disable_snapshotting": False,
                    "read_only": False,
                    "slot": 0,
                    "tiering_priority_factor": 8,
                    "type": "virtio_disk",
                    "uuid": "block-uuid-1",
                },
            ],
        }

        self.device_snapshots = [
            {
                "uuid": "block-uuid-1",
            },
        ]

        self.vm_snapshot = VMSnapshot(
            snapshot_uuid="test",
            vm_name=self.vm["name"],
            vm=self.vm,
            device_snapshots=self.device_snapshots,
            timestamp=123,
            label="snapshot",
            type="USER",
            automated_trigger_timestamp=111,
            local_retain_until_timestamp=222,
            remote_retain_until_timestamp=333,
            block_count_diff_from_serial_number=444,
            replication=True,
        )
        self.from_hypercore_dict = dict(
            uuid=self.vm_snapshot.snapshot_uuid,
            domainUUID=self.vm_snapshot.vm["uuid"],
            domain={
                "name": self.vm_snapshot.vm["name"],
                "snapshotSerialNumber": self.vm_snapshot.vm["snapshot_serial_number"],
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
            deviceSnapshots=self.device_snapshots,
            timestamp=self.vm_snapshot.timestamp,
            label=self.vm_snapshot.label,
            type=self.vm_snapshot.type,
            automatedTriggerTimestamp=self.vm_snapshot.automated_trigger_timestamp,
            localRetainUntilTimestamp=self.vm_snapshot.local_retain_until_timestamp,
            remoteRetainUntilTimestamp=self.vm_snapshot.remote_retain_until_timestamp,
            blockCountDiffFromSerialNumber=self.vm_snapshot.block_count_diff_from_serial_number,
            replication=self.vm_snapshot.replication,
        )
        self.to_hypercore_dict = dict(
            uuid=self.vm_snapshot.snapshot_uuid,
            domainUUID=None,
            label=self.vm_snapshot.label,
            type=self.vm_snapshot.type.upper(),
            replication=True,
            localRetainUntilTimestamp=222,
            remoteRetainUntilTimestamp=333,
        )
        self.ansible_dict = dict(
            snapshot_uuid=self.vm_snapshot.snapshot_uuid,
            vm_name=self.vm_snapshot.vm_name,
            vm=self.vm_snapshot.vm,
            device_snapshots=self.vm_snapshot.device_snapshots,
            timestamp=self.vm_snapshot.timestamp,
            label=self.vm_snapshot.label,
            type=self.vm_snapshot.type,
            automated_trigger_timestamp=self.vm_snapshot.automated_trigger_timestamp,
            local_retain_until_timestamp=VMSnapshot.convert_from_unix_timestamp(
                self.vm_snapshot.local_retain_until_timestamp
            ),
            remote_retain_until_timestamp=VMSnapshot.convert_from_unix_timestamp(
                self.vm_snapshot.remote_retain_until_timestamp
            ),
            block_count_diff_from_serial_number=self.vm_snapshot.block_count_diff_from_serial_number,
            replication=self.vm_snapshot.replication,
        )

        self.disk_hypercore = dict(
            allocation=0,
            uuid="new-block-uuid",
            cacheMode="NONE",
            capacity=100000595968,
            createdTimestamp=0,
            disableSnapshotting=False,
            mountPoints=[],
            name="",
            path="scribe/new-block-uuid",
            physical=0,
            readOnly=False,
            shareUUID="",
            slot=21,
            tieringPriorityFactor=8,
            type="VIRTIO_DISK",
            virDomainUUID="vm-uuid",
        )

        self.disk_ansible = dict(
            uuid="new-block-uuid",
            slot=21,
            type="virtio_disk",
            vm_uuid="vm-uuid",
            size=100000595968,
        )

    def test_vm_snapshot_to_hypercore(self):
        to_hypercore = self.vm_snapshot.to_hypercore()
        assert to_hypercore == self.to_hypercore_dict

    def test_vm_snapshot_from_hypercore_dict_not_empty(self):
        vm_snapshot_from_hypercore = VMSnapshot.from_hypercore(self.from_hypercore_dict)

        print(vm_snapshot_from_hypercore)
        print("\n")
        print(self.vm_snapshot)

        assert vm_snapshot_from_hypercore == self.vm_snapshot

    def test_vm_snapshot_from_hypercore_dict_empty(self):
        assert VMSnapshot.from_hypercore([]) is None

    def test_vm_snapshot_to_ansible(self):
        to_ansible = self.vm_snapshot.to_ansible()
        assert to_ansible == self.ansible_dict

    def test_vm_snapshot_from_ansible(self):
        vm_snapshot_from_ansible = VMSnapshot.from_ansible(self.ansible_dict)
        assert vm_snapshot_from_ansible == VMSnapshot(
            snapshot_uuid=vm_snapshot_from_ansible.snapshot_uuid,
            vm=vm_snapshot_from_ansible.vm,
            device_snapshots=vm_snapshot_from_ansible.device_snapshots,
            label=vm_snapshot_from_ansible.label,
            type=vm_snapshot_from_ansible.type,
        )

    def test_get_snapshot_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(**self.from_hypercore_dict)
        vm_snapshot_from_hypercore = VMSnapshot.get_snapshot_by_uuid(
            snapshot_uuid="test",
            rest_client=rest_client,
        )
        assert vm_snapshot_from_hypercore == self.vm_snapshot

    @pytest.mark.parametrize(
        ("query",),
        [
            (
                dict(
                    uuid="test",
                )
            ),
            (
                dict(
                    domainUUID="vm-uuid",
                )
            ),
            (
                dict(
                    label="snapshot",
                )
            ),
            (
                dict(
                    type="USER",
                )
            ),
        ],
    )
    def test_get_snapshots_by_query(self, rest_client, query):
        rest_client.list_records.return_value = [dict(**self.from_hypercore_dict)]
        vm_snapshot_from_hypercore = VMSnapshot.get_snapshots_by_query(
            query=query,
            rest_client=rest_client,
        )
        print(vm_snapshot_from_hypercore)
        print("\n")
        print([self.ansible_dict])
        assert vm_snapshot_from_hypercore == [self.ansible_dict]

    # =============================
    # "filter_snapshots_by_params" function is already being tested with integration tests... should I still make unit tests for it?
    # =============================

    def test_hypercore_disk_to_ansible(self):
        hypercore_disk_to_ansible = VMSnapshot.hypercore_disk_to_ansible(
            self.disk_hypercore
        )
        assert hypercore_disk_to_ansible == self.disk_ansible

    def test_get_vm_disk_info_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(**self.disk_hypercore)
        vm_disk_info_from_hypercore = VMSnapshot.get_vm_disk_info_by_uuid(
            disk_uuid="new-block-uuid",
            rest_client=rest_client,
        )
        assert vm_disk_info_from_hypercore == self.disk_ansible

    def test_get_vm_disk_info(self, rest_client):
        rest_client.get_record.return_value = dict(**self.disk_hypercore)
        vm_disk_info_from_hypercore = VMSnapshot.get_vm_disk_info(
            vm_uuid="new-block-uuid",
            slot=21,
            _type="VIRTIO_DISK",
            rest_client=rest_client,
        )
        assert vm_disk_info_from_hypercore == self.disk_ansible

    def test_get_snapshot_disk(self):
        snapshot_disk = VMSnapshot.get_snapshot_disk(
            vm_snapshot=self.ansible_dict,
            slot=0,
            _type="virtio_disk",
        )

        assert snapshot_disk == self.ansible_dict["vm"]["disks"][0]

    def test_get_external_vm_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(
            name="test-vir-domain",
            uuid="test-vir-domain-uuid",
        )
        external_vm_uuid = VMSnapshot.get_external_vm_uuid(
            vm_name="test-vir-domain",
            rest_client=rest_client,
        )
        assert external_vm_uuid == "test-vir-domain-uuid"
