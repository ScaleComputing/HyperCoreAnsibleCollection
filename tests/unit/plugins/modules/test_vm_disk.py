# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_disk
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM
from ansible_collections.scale_computing.hypercore.plugins.module_utils.iso import ISO
from ansible_collections.scale_computing.hypercore.plugins.module_utils.disk import Disk
from ansible_collections.scale_computing.hypercore.plugins.module_utils.errors import (
    ScaleComputingError,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestGetVMByName:
    def test_get_vm_by_name_disks_empty(self, create_module, rest_client):
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

        rest_client.get_record.side_effect = [
            dict(
                uuid="id",
                name="VM-name",
                tags="XLAB-test-tag1,XLAB-test-tag2",
                description="desc",
                mem=42,
                state="RUNNING",
                numVCPU=2,
                netDevs=[],
                blockDevs=[],
                bootDevices=None,
                attachGuestToolsISO=False,
                operatingSystem=None,
                affinityStrategy=dict(
                    preferredNodeUUID="",
                    strictAffinity=False,
                    backupNodeUUID="",
                ),
                nodeUUID="node-id",
            ),
            dict(
                uuid="node-id",
                backplaneIP="10.0.0.1",
                lanIP="10.0.0.1",
                peerID=1,
            ),
            dict(
                uuid="node-id",
                backplaneIP="10.0.0.1",
                lanIP="10.0.0.1",
                peerID=1,
            ),
        ]

        vm = VM(
            attach_guest_tools_iso=False,
            boot_devices=[],
            description="desc",
            disks=[],
            memory=42,
            name="VM-name",
            nics=[],
            vcpu=2,
            operating_system=None,
            power_state="started",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            uuid="id",
            node_affinity=dict(
                strict_affinity=False,
                preferred_node=None,
                backup_node=None,
            ),
            node_uuid="node-id",
        )

        result = vm_disk.get_vm_by_name(module, rest_client)
        assert result == (vm, [])

    def test_get_vm_by_name_disks_present(self, create_module, rest_client):
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

        rest_client.get_record.return_value = dict(
            uuid="id",
            name="VM-name",
            tags="XLAB-test-tag1,XLAB-test-tag2",
            description="desc",
            mem=42,
            state="RUNNING",
            numVCPU=2,
            netDevs=[],
            blockDevs=[
                dict(
                    uuid="id",
                    virDomainUUID="vm-id",
                    type="VIRTIO_DISK",
                    cacheMode="NONE",
                    capacity=4200,
                    slot=0,
                    name="jc1-disk-0",
                    disableSnapshotting=False,
                    tieringPriorityFactor=8,
                    mountPoints=[],
                    readOnly=False,
                )
            ],
            bootDevices=None,
            attachGuestToolsISO=False,
            operatingSystem=None,
            affinityStrategy=dict(
                preferredNodeUUID="",
                strictAffinity=False,
                backupNodeUUID="",
            ),
            nodeUUID="node-id",
        )

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
            node_affinity=dict(
                strict_affinity=False,
                preferred_node=None,
                backup_node=None,
            ),
            node_uuid="node-id",
        )

        result = vm_disk.get_vm_by_name(module, rest_client)
        assert result == (
            vm,
            [
                dict(
                    type="virtio_disk",
                    disk_slot=0,
                    size=4200,
                    uuid="id",
                    vm_uuid="vm-id",
                    cache_mode="none",
                    name="jc1-disk-0",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    mount_points=[],
                    read_only=False,
                )
            ],
        )


class TestCreateBlockDevice:
    def test_create_block_device(self, create_module, rest_client, vm, task_wait):
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
        vm = VM(name="vm-name", memory=42, vcpu=2, uuid="id")
        desired_disk = Disk(
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

        rest_client.create_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
        }

        result = vm_disk.create_block_device(module, rest_client, vm, desired_disk)
        rest_client.create_record.assert_called_with(
            "/rest/v1/VirDomainBlockDevice",
            dict(
                uuid="id",
                virDomainUUID="id",
                type="VIRTIO_DISK",
                cacheMode="NONE",
                capacity=4200,
                name="jc1-disk-0",
                tieringPriorityFactor=8,
            ),
            False,
        )
        assert result == "disk-id"


class TestISOImageManagement:
    def test_iso_image_management_attach(self, create_module, rest_client, task_wait):
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

        iso = ISO(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            ready_for_insert=False,
            path="scribe/123",
        )
        uuid = "disk_id"
        attach = True
        result = vm_disk.iso_image_management(module, rest_client, iso, uuid, attach)
        rest_client.update_record.assert_called_with(
            "/rest/v1/VirDomainBlockDevice/disk_id",
            dict(
                path="scribe/123",
                name="ISO-test-name",
            ),
            False,
        )
        assert result is None

    def test_iso_image_management_detach(self, create_module, rest_client, task_wait):
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

        iso = ISO(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            ready_for_insert=False,
            path="scribe/123",
        )
        uuid = "disk_id"
        attach = False
        result = vm_disk.iso_image_management(module, rest_client, iso, uuid, attach)
        rest_client.update_record.assert_called_with(
            "/rest/v1/VirDomainBlockDevice/disk_id",
            dict(
                path="",
                name="",
            ),
            False,
        )
        assert result is None


class TestUpdateBlockDevice:
    def test_update_block_device(self, create_module, rest_client, task_wait):
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

        existing_disk = Disk(
            type="virtio_disk",
            slot=0,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            size=5000,
            name="jc1-disk-0",
            disable_snapshotting=True,
            tiering_priority_factor=64,
            mount_points=[],
            read_only=False,
        )

        desired_disk = Disk(
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

        vm = VM(name="vm-name", memory=42, vcpu=2, uuid="id")
        result = vm_disk.update_block_device(
            module, rest_client, desired_disk, existing_disk, vm
        )

        rest_client.update_record.assert_called_with(
            "/rest/v1/VirDomainBlockDevice/id",
            {
                "cacheMode": "NONE",
                "capacity": 4200,
                "name": "jc1-disk-0",
                "tieringPriorityFactor": 8,
                "type": "VIRTIO_DISK",
                "uuid": "id",
                "virDomainUUID": "id",
            },
            False,
        )

        assert result is None


class TestForceRemoveAllDisks:
    def test_force_remove_all_disks_disks_present(
        self, create_module, rest_client, task_wait
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                items=[],
            )
        )

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
            name="VM-name-unique",
            nics=[],
            vcpu=2,
            operating_system=None,
            power_state="started",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            uuid="id",
        )

        disks_before = [
            dict(
                type="virtio_disk",
                disk_slot=0,
                size=4200,
                uuid="id",
                vm_uuid="vm-id",
                cache_mode="none",
                name="jc1-disk-0",
                disable_snapshotting=False,
                tiering_priority_factor=8,
                mount_points=[],
                read_only=False,
            )
        ]

        rest_client.delete_record.side_effect = [
            {
                "taskTag": "123",
                "createdUUID": "",
            },
            {
                "taskTag": "124",
                "createdUUID": "",
            },
        ]

        result = vm_disk.force_remove_all_disks(module, rest_client, vm, disks_before)
        assert result == (
            True,
            [],
            dict(
                before=[
                    dict(
                        type="virtio_disk",
                        disk_slot=0,
                        size=4200,
                        uuid="id",
                        vm_uuid="vm-id",
                        cache_mode="none",
                        name="jc1-disk-0",
                        disable_snapshotting=False,
                        tiering_priority_factor=8,
                        mount_points=[],
                        read_only=False,
                    )
                ],
                after=[],
            ),
        )

    def test_force_remove_all_disks_items_not_empty_list(
        self, create_module, rest_client
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                items=None,
            )
        )
        vm = "Not important"
        disks_before = "Not important"
        with pytest.raises(ScaleComputingError, match="force"):
            vm_disk.force_remove_all_disks(module, rest_client, vm, disks_before)


class TestEnsurePresentOrSet:
    def test_ensure_present_create_new_disk(
        self, create_module, rest_client, task_wait
    ):
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
                force=0,
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
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    {
                        "uuid": "disk-id",
                        "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                        "cacheMode": "none",
                        "capacity": 345,
                        "name": None,
                        "slot": 1,
                        "type": "VIRTIO_DISK",
                        "disableSnapshotting": True,
                        "tieringPriorityFactor": 1,
                        "mountPoints": None,
                        "readOnly": False,
                    }
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
            },
        ]
        rest_client.create_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
        }
        results = vm_disk.ensure_present_or_set(module, rest_client)
        assert results == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": True,
                    "disk_slot": 1,
                    "mount_points": None,
                    "name": None,
                    "read_only": False,
                    "size": 345,
                    "tiering_priority_factor": 1,
                    "type": "virtio_disk",
                    "uuid": "disk-id",
                    "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                }
            ],
            {
                "after": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": True,
                        "disk_slot": 1,
                        "mount_points": None,
                        "name": None,
                        "read_only": False,
                        "size": 345,
                        "tiering_priority_factor": 1,
                        "type": "virtio_disk",
                        "uuid": "disk-id",
                        "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                    }
                ],
                "before": [],
            },
        )

    def test_ensure_present_update_test_idempotency(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, size=4200, type="virtio_disk")],
                state="present",
                force=0,
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
            },
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
            },
        ]
        results = vm_disk.ensure_present_or_set(module, rest_client)
        assert results == (
            False,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 1,
                    "mount_points": [],
                    "name": "jc1-disk-0",
                    "read_only": False,
                    "size": 4200,
                    "tiering_priority_factor": 8,
                    "type": "virtio_disk",
                    "uuid": "id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
        )

    def test_ensure_present_update_record(self, create_module, rest_client, task_wait):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, size=5000, type="virtio_disk")],
                state="present",
                force=0,
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
            },
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "name": "XLAB_test_vm",
                "blockDevs": [
                    dict(
                        uuid="id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=5000,
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
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
        }
        results = vm_disk.ensure_present_or_set(module, rest_client)
        assert results == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 1,
                    "mount_points": [],
                    "name": "jc1-disk-0",
                    "read_only": False,
                    "size": 5000,
                    "tiering_priority_factor": 8,
                    "type": "virtio_disk",
                    "uuid": "id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 5000,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
        )

    def test_ensure_present_attach_iso_cdrom_existing(
        self, create_module, rest_client, task_wait
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
                force=0,
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
                        name="",
                        disableSnapshotting=False,
                        tieringPriorityFactor=8,
                        mountPoints=[],
                        readOnly=False,
                        path="scribe/123",
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
                "blockDevs": [
                    dict(
                        uuid="id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=5000,
                        slot=1,
                        name="iso-name",
                        disableSnapshotting=False,
                        tieringPriorityFactor=8,
                        mountPoints=[],
                        readOnly=False,
                        path="scribe/123",
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
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
        }
        results = vm_disk.ensure_present_or_set(module, rest_client)
        assert results == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 1,
                    "mount_points": [],
                    "name": "iso-name",
                    "read_only": False,
                    "size": 5000,
                    "tiering_priority_factor": 8,
                    "type": "virtio_disk",
                    "uuid": "id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "name": "iso-name",
                        "read_only": False,
                        "size": 5000,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "name": "",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "ide_cdrom",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
        )

    def test_ensure_present_attach_iso_cdrom_absent(
        self, create_module, rest_client, task_wait
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
                force=0,
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
                "blockDevs": [
                    dict(
                        uuid="id",
                        virDomainUUID="vm-id",
                        type="VIRTIO_DISK",
                        cacheMode="NONE",
                        capacity=5000,
                        slot=1,
                        name="iso-name",
                        disableSnapshotting=False,
                        tieringPriorityFactor=8,
                        mountPoints=[],
                        readOnly=False,
                        path="scribe/123",
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
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "",
        }
        rest_client.create_record.return_value = {
            "taskTag": "124",
            "createdUUID": "disk-id",
        }
        results = vm_disk.ensure_present_or_set(module, rest_client)
        assert results == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 1,
                    "mount_points": [],
                    "name": "iso-name",
                    "read_only": False,
                    "size": 5000,
                    "tiering_priority_factor": 8,
                    "type": "virtio_disk",
                    "uuid": "id",
                    "vm_uuid": "vm-id",
                }
            ],
            {
                "after": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "name": "iso-name",
                        "read_only": False,
                        "size": 5000,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
                "before": [],
            },
        )

    # ensure_present uses only a subset of code of ensure_set. So not testing ensure set again, setting the created
    # disks to empty list as this is tested in this class in methods above already
    def test_ensure_set_force_remove_disks(self, create_module, rest_client, task_wait):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name",
                items=[],
                state="set",
                force=1,
            )
        )

        rest_client.get_record.return_value = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [
                dict(
                    uuid="id",
                    virDomainUUID="vm-id",
                    type="VIRTIO_DISK",
                    cacheMode="NONE",
                    capacity=5000,
                    slot=1,
                    name="iso-name",
                    disableSnapshotting=False,
                    tieringPriorityFactor=8,
                    mountPoints=[],
                    readOnly=False,
                    path="scribe/123",
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
        }
        result = vm_disk.ensure_present_or_set(module, rest_client)
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
                        "name": "iso-name",
                        "read_only": False,
                        "size": 5000,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
        )

    def test_ensure_set_remove_unused_disk(self, create_module, rest_client, task_wait):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
                force=0,
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
            },
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
            },
        ]

        rest_client.delete_record.return_value = {
            "taskTag": "123",
            "createdUUID": "",
        }

        result = vm_disk.ensure_present_or_set(module, rest_client)

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
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
        )


class TestEnsureAbsent:
    def test_ensure_absent_no_disk_present(self, create_module, rest_client):
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
            },
        ]
        results = vm_disk.ensure_absent(module, rest_client)
        assert results == (
            False,
            [],
            {
                "after": [],
                "before": [],
            },
        )

    def test_ensure_absent_delete_record(self, create_module, rest_client, task_wait):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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
            },
        ]
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
                        "mount_points": [],
                        "name": "jc1-disk-0",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
        )

    def test_ensure_absent_cdrom_name_in_desired_disk_and_query(
        self, create_module, rest_client, task_wait
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
            },
        ]
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "",
        }
        results = vm_disk.ensure_absent(module, rest_client)
        assert results == (
            False,
            [],
            {
                "after": [],
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
                        "mount_points": [],
                        "name": "iso-name",
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "ide_cdrom",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
        )

    def test_ensure_absent_cdrom_no_name_error(
        self, create_module, rest_client, task_wait
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, type="ide_cdrom")],
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
                        name="",
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
            },
        ]
        with pytest.raises(ScaleComputingError, match="ISO"):
            vm_disk.ensure_absent(module, rest_client)


class TestNotUsedDisks:
    def test_delete_not_used_disks_no_deletion(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, type="virtio_disk")],
                state="present",
                force=0,
            )
        )

        rest_client.get_record.return_value = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [
                {
                    "uuid": "disk-id",
                    "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                    "cacheMode": "none",
                    "capacity": 356,
                    "name": None,
                    "slot": 1,
                    "type": "VIRTIO_DISK",
                    "disableSnapshotting": True,
                    "tieringPriorityFactor": 1,
                    "mountPoints": None,
                    "readOnly": False,
                }
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
        }

        changed = False
        changed = vm_disk.delete_not_used_disks(module, rest_client, changed)
        rest_client.delete_record.assert_not_called()
        assert not changed

    def test_delete_not_used_disks_deletion(
        self, create_module, rest_client, task_wait
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=2, type="ide_cdrom")],
                state="present",
                force=0,
            )
        )

        rest_client.get_record.return_value = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [
                {
                    "uuid": "disk-id",
                    "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                    "cacheMode": "none",
                    "capacity": 356,
                    "name": None,
                    "slot": 1,
                    "type": "VIRTIO_DISK",
                    "disableSnapshotting": True,
                    "tieringPriorityFactor": 1,
                    "mountPoints": None,
                    "readOnly": False,
                }
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
        }

        changed = False
        rest_client.delete_record.return_value = {
            "taskTag": "123",
            "createdUUID": "",
        }
        changed = vm_disk.delete_not_used_disks(module, rest_client, changed)
        rest_client.delete_record.assert_called_with(
            "/rest/v1/VirDomainBlockDevice/disk-id",
            False,
        )
        assert changed
