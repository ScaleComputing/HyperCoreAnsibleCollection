# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    vm_boot_devices,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestEnsureAbsent:
    def test_ensure_absent_no_source_object_present(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=4200,
                        slot=444,
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
                "bootDevices": ["disk-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=4200,
                        slot=444,
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
                "bootDevices": ["disk-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
                "sourceVirDomainUUID": "",
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = vm_boot_devices.ensure_absent(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (
            False,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 444,
                    "iso_name": "jc1-disk-0",
                    "mount_points": [],
                    "read_only": False,
                    "size": 4200,
                    "tiering_priority_factor": 4,
                    "type": "virtio_disk",
                    "uuid": "disk-id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 444,
                        "iso_name": "jc1-disk-0",
                        "mount_points": [],
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 4,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 444,
                        "iso_name": "jc1-disk-0",
                        "mount_points": [],
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 4,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
            False,
        )

    def test_ensure_absent_uuid_not_in_boot_devices(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "sourceVirDomainUUID": "",
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = vm_boot_devices.ensure_absent(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (False, [], {"after": [], "before": []}, False)

    def test_ensure_absent_update_successful(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                shutdown_timeout=10,
                force_reboot=False,
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "bootDevices": ["disk-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "sourceVirDomainUUID": "",
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
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
        result = vm_boot_devices.ensure_absent(module, rest_client)
        rest_client.update_record.assert_called_once()
        assert result == (
            True,
            [],
            {
                "after": [],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "iso_name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 4,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
            False,
        )


class TestEnsurePresent:
    def test_ensure_present_no_source_object_present(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=4200,
                        slot=444,
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
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=4200,
                        slot=444,
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
                "sourceVirDomainUUID": "",
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = vm_boot_devices.ensure_present(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (False, [], {"after": [], "before": []}, False)

    def test_ensure_present_item_first(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                shutdown_timeout=10,
                force_reboot=False,
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
                first=True,
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "bootDevices": ["disk-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
                "sourceVirDomainUUID": "",
            },
        ]

        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
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
        result = vm_boot_devices.ensure_present(module, rest_client)
        rest_client.update_record.assert_called_once()
        assert result == (
            True,
            [
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
                    "uuid": "disk-id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
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
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [],
            },
            False,
        )

    def test_ensure_present_item_not_first_boot_order_already_present(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
                first=False,
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "bootDevices": ["disk-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "bootDevices": ["disk-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
                "sourceVirDomainUUID": "",
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = vm_boot_devices.ensure_present(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (
            False,
            [
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
                    "uuid": "disk-id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
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
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
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
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
            False,
        )

    def test_ensure_present_item_not_first_boot_order_updated(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                shutdown_timeout=10,
                force_reboot=False,
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
                first=False,
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "bootDevices": ["disk-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
                "sourceVirDomainUUID": "",
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
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
        result = vm_boot_devices.ensure_present(module, rest_client)
        rest_client.update_record.assert_called_once()
        assert result == (
            True,
            [
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
                    "uuid": "disk-id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
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
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [],
            },
            False,
        )


class TestEnsureSet:
    def test_ensure_set_no_source_object_present(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=4200,
                        slot=444,
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
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=4200,
                        slot=444,
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
                "sourceVirDomainUUID": "",
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = vm_boot_devices.ensure_set(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (False, [], {"after": [], "before": []}, False)

    def test_ensure_set_source_object_present(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                shutdown_timeout=10,
                force_reboot=False,
                items=[
                    dict(
                        type="virtio_disk",
                        disk_slot=1,
                        nic_vlan=None,
                        iso_name=None,
                    )
                ],
            )
        )

        rest_client.get_record.side_effect = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "sourceVirDomainUUID": "",
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="disk-id",
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
                "bootDevices": ["disk-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
                "machineType": "scale-7.2",
                "sourceVirDomainUUID": "",
            },
            dict(
                uuid="disk-id",
                virDomainUUID="vm-id",
                type="VIRTIO_DISK",
                cacheMode="NONE",
                capacity=4200,
                slot=444,
                name="jc1-disk-0",
                disableSnapshotting=False,
                tieringPriorityFactor=8,
                mountPoints=[],
                readOnly=False,
            ),
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
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
        result = vm_boot_devices.ensure_set(module, rest_client)
        rest_client.update_record.assert_called_once()
        assert result == (
            True,
            [
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
                    "uuid": "disk-id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
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
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [],
            },
            False,
        )
