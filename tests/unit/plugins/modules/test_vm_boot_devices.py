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
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM
from ansible_collections.scale_computing.hypercore.plugins.module_utils.disk import Disk

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestGetSourceObjectQuery:
    def test_get_source_object_query(self):
        desired_source_object = dict(
            disk_slot=2,
            nic_vlan=None,
            iso_name="iso-image-name",
        )
        assert vm_boot_devices.get_source_object_query(desired_source_object) == dict(
            disk_slot=2,
            name="iso-image-name",
        )


class TestGetVMDevice:
    def test_get_vm_device_type_not_nic(self, create_module, rest_client):
        vm = VM(
            attach_guest_tools_iso=False,
            boot_devices=[],
            description="desc",
            disks=[
                Disk(
                    type="virtio_disk",
                    slot=0,
                    uuid="id",
                    vm_uuid="vm-id",
                    cache_mode="none",
                    size=4200,
                    name="jc1-disk-0",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    mount_points=[],
                    read_only=False,
                )
            ],
            memory=42,
            name="VM-name",
            nics=[],
            vcpu=2,
            operating_system=None,
            power_state="started",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            uuid="id",
        )

        desired_source_object = dict(
            disk_slot=0,
            nic_vlan=None,
            iso_name="jc1-disk-0",
            type="virtio_disk",
        )

        source_object_ansible = vm_boot_devices.get_vm_device(vm, desired_source_object)

        assert source_object_ansible == {
            "cache_mode": "none",
            "disable_snapshotting": False,
            "disk_slot": 0,
            "mount_points": [],
            "name": "jc1-disk-0",
            "read_only": False,
            "size": 4200,
            "tiering_priority_factor": 8,
            "type": "virtio_disk",
            "uuid": "id",
            "vm_uuid": "vm-id",
        }


class TestUpdateBootDeviceOrder:
    def test_update_boot_device_order(self, create_module, rest_client, task_wait):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
            )
        )

        uuid = "vm-id"
        boot_order = ["device1-id", "device2-id"]

        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
        }
        vm_boot_devices.update_boot_device_order(module, rest_client, uuid, boot_order)
        rest_client.update_record.assert_called_with(
            "/rest/v1/VirDomain/vm-id",
            dict(
                bootDevices=["device1-id", "device2-id"],
                uuid="vm-id",
            ),
            False,
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
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
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
                    "mount_points": [],
                    "name": "jc1-disk-0",
                    "read_only": False,
                    "size": 4200,
                    "tiering_priority_factor": 8,
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
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
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
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
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
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None

        result = vm_boot_devices.ensure_absent(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (False, [], {"after": [], "before": []})

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
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
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
                        "disk_slot": 444,
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
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
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None

        result = vm_boot_devices.ensure_present(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (False, [], {"after": [], "before": []})

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
                "bootDevices": ["boot-order-other-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
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
                "bootDevices": ["disk-id", "boot-order-other-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
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
            dict(
                uuid="boot-order-other-id",
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

        result = vm_boot_devices.ensure_present(module, rest_client)
        rest_client.update_record.assert_called_once()
        assert result == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 444,
                    "mount_points": [],
                    "name": "jc1-disk-0",
                    "read_only": False,
                    "size": 4200,
                    "tiering_priority_factor": 8,
                    "type": "virtio_disk",
                    "uuid": "disk-id",
                    "vm_uuid": "vm-id",
                },
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 444,
                    "mount_points": [],
                    "name": "jc1-disk-0",
                    "read_only": False,
                    "size": 4200,
                    "tiering_priority_factor": 8,
                    "type": "virtio_disk",
                    "uuid": "boot-order-other-id",
                    "vm_uuid": "vm-id",
                },
            ],
            {
                "after": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 444,
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    },
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 444,
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "boot-order-other-id",
                        "vm_uuid": "vm-id",
                    },
                ],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 444,
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
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

        result = vm_boot_devices.ensure_present(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (
            False,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 444,
                    "mount_points": [],
                    "name": "jc1-disk-0",
                    "read_only": False,
                    "size": 4200,
                    "tiering_priority_factor": 8,
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
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
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
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
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

        result = vm_boot_devices.ensure_present(module, rest_client)
        rest_client.update_record.assert_called_once()
        assert result == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 444,
                    "mount_points": [],
                    "name": "jc1-disk-0",
                    "read_only": False,
                    "size": 4200,
                    "tiering_priority_factor": 8,
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
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [],
            },
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
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None

        result = vm_boot_devices.ensure_set(module, rest_client)
        rest_client.update_record.assert_not_called()
        assert result == (False, [], {"after": [], "before": []})

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
                "bootDevices": ["boot-order-other-id"],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "preferredNodeUUID": "",
                    "strictAffinity": False,
                    "backupNodeUUID": "",
                },
                "nodeUUID": "node-id",
                "snapshotScheduleUUID": "snapshot_schedule_id",
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

        result = vm_boot_devices.ensure_set(module, rest_client)
        rest_client.update_record.assert_called_once()
        assert result == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 444,
                    "mount_points": [],
                    "name": "jc1-disk-0",
                    "read_only": False,
                    "size": 4200,
                    "tiering_priority_factor": 8,
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
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
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
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
        )
