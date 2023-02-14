# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_disk
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestEnsureAbsent:
    def test_ensure_absent_no_disk_present(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, size=356, type="virtio_disk")],
                state="present",
            )
        )
        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [],
                "netDevs": [],
                "stats": "bla",
                "tags": "XLAB,test",
                "description": "test vm",
                "mem": 23424234,
                "state": "RUNNING",
                "numVCPU": 2,
                "bootDevices": [],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [],
                "netDevs": [],
                "stats": "bla",
                "tags": "XLAB,test",
                "description": "test vm",
                "mem": 23424234,
                "state": "RUNNING",
                "numVCPU": 2,
                "bootDevices": [],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        results = vm_disk.ensure_absent(module, rest_client)
        assert results == (
            False,
            [],
            {
                "after": [],
                "before": [],
            },
            False,
        )

    def test_ensure_absent_delete_record(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                shutdown_timeout=10,
                force_reboot=False,
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, type="virtio_disk")],
                state="present",
            )
        )
        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=4200,
                        slot=1,
                        name="jc1-disk-0",
                        disableSnapshotting=False,
                        tieringPriorityFactor=8,
                        mountPoints=[],
                        readOnly=False,
                    )
                ],
                "netDevs": [],
                "stats": "bla",
                "tags": "XLAB,test",
                "description": "test vm",
                "mem": 23424234,
                "state": "RUNNING",
                "numVCPU": 2,
                "bootDevices": [],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [],
                "netDevs": [],
                "stats": "bla",
                "tags": "XLAB,test",
                "description": "test vm",
                "mem": 23424234,
                "state": "RUNNING",
                "numVCPU": 2,
                "bootDevices": [],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.do_shutdown_steps"
        ).return_value = None
        results = vm_disk.ensure_absent(module, rest_client)
        assert results == (
            True,
            [],
            {
                "after": [],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "iso_name": "jc1-disk-0",
                        "mount_points": [],
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 4,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
            False,
        )

    def test_ensure_absent_cdrom_name_in_desired_disk_and_query(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, type="ide_cdrom", iso_name="iso-name")],
                state="present",
            )
        )
        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="id",
                        virDomainUUID="vm-id",
                        type="IDE_CDROM",
                        cacheMode="NONE",
                        capacity=4200,
                        slot=1,
                        name="iso-name",
                        disableSnapshotting=False,
                        tieringPriorityFactor=8,
                        mountPoints=[],
                        readOnly=False,
                    )
                ],
                "netDevs": [],
                "stats": "bla",
                "tags": "XLAB,test",
                "description": "test vm",
                "mem": 23424234,
                "state": "RUNNING",
                "numVCPU": 2,
                "bootDevices": [],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
            },
            {
                "uuid": "iso-uuid",
                "name": "iso-name",
                "size": 123,
                "mounts": [],
                "readyForInsert": True,
                "path": "scribe/123",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [],
                "netDevs": [],
                "stats": "bla",
                "tags": "XLAB,test",
                "description": "test vm",
                "mem": 23424234,
                "state": "RUNNING",
                "numVCPU": 2,
                "bootDevices": [],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.do_shutdown_steps"
        ).return_value = None
        results = vm_disk.ensure_absent(module, rest_client)
        assert results == (
            True,
            [],
            {
                "after": [],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "iso_name": "iso-name",
                        "mount_points": [],
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 4,
                        "type": "ide_cdrom",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
            False,
        )
