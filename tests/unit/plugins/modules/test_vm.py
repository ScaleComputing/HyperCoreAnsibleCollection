from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm
from ansible_collections.scale_computing.hypercore.plugins.module_utils.errors import (
    ScaleComputingError,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestEnsureAbsent:
    def test_ensure_absent_record_present_power_state_shutdown(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-unique-name",
                description=None,
                memory=42,
                vcpu=2,
                power_state="started",
                state="absent",
                tags=None,
                disks=None,
                nics=None,
                boot_devices=None,
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
            ),
        )

        rest_client.get_record.return_value = dict(
            uuid="id",
            nodeUUID="",
            name="VM-name-unique",
            tags="XLAB-test-tag1,XLAB-test-tag2",
            description="desc",
            mem=42,
            state="SHUTDOWN",
            numVCPU=2,
            netDevs=[],
            blockDevs=[],
            bootDevices=[],
            attachGuestToolsISO=False,
            operatingSystem=None,
            affinityStrategy={
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            snapshotScheduleUUID="shapshot-id",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        rest_client.delete_record.return_value = None

        result = vm.ensure_absent(module, rest_client)

        rest_client.delete_record.assert_called_once()
        assert result == (
            True,
            [
                {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "shutdown",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                }
            ],
            {
                "after": None,
                "before": {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "shutdown",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                },
            },
        )

    def test_ensure_absent_record_present_power_state_not_shutdown(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-unique-name",
                description=None,
                memory=42,
                vcpu=2,
                power_state="started",
                state="absent",
                tags=None,
                disks=None,
                nics=None,
                boot_devices=None,
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
            ),
        )

        rest_client.get_record.return_value = dict(
            uuid="id",
            nodeUUID="",
            name="VM-name-unique",
            tags="XLAB-test-tag1,XLAB-test-tag2",
            description="desc",
            mem=42,
            state="RUNNING",
            numVCPU=2,
            netDevs=[],
            blockDevs=[],
            bootDevices=[],
            attachGuestToolsISO=False,
            operatingSystem=None,
            affinityStrategy={
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            snapshotScheduleUUID="snapshot_schedule_uuid",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        rest_client.delete_record.return_value = None
        rest_client.create_record.return_value = {
            "taskTag": 123,
            "createdUUID": "",
        }

        result = vm.ensure_absent(module, rest_client)

        rest_client.delete_record.assert_called_once()
        assert result == (
            True,
            [
                {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "started",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                }
            ],
            {
                "after": None,
                "before": {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "started",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                },
            },
        )

    def test_ensure_absent_record_absent(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="VM-unique-name",
                description=None,
                memory=42,
                vcpu=2,
                power_state="started",
                state="absent",
                tags=None,
                disks=None,
                nics=None,
                boot_devices=None,
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
            ),
        )
        rest_client.get_record.return_value = None

        result = vm.ensure_absent(module, rest_client)

        assert result == (False, [], dict())


class TestEnsurePresent:
    def test_ensure_present_record_already_present(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-unique-name",
                description=None,
                memory=42,
                vcpu=2,
                power_state="started",
                state="present",
                tags="",
                disks=None,
                nics=None,
                boot_devices=None,
                cloud_init=None,
                attach_guest_tools_iso=None,
                cloud_init_data=None,
            ),
        )

        rest_client.get_record.return_value = dict(
            uuid="id",
            nodeUUID="",
            name="VM-name-unique",
            tags="XLAB-test-tag1,XLAB-test-tag2",
            description="desc",
            mem=42,
            state="SHUTDOWN",
            numVCPU=2,
            netDevs=[],
            blockDevs=[],
            bootDevices=[],
            attachGuestToolsISO=False,
            operatingSystem=None,
            affinityStrategy={
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            snapshotScheduleUUID="snapshot_schedule_uuid",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        with pytest.raises(ScaleComputingError, match="not unique"):
            vm.ensure_present(module, rest_client)

    def test_ensure_present_no_boot_devices_power_state_is_shutdown(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                description="desc",
                memory=42,
                vcpu=2,
                power_state="shutdown",
                state="present",
                tags="",
                disks=[],
                nics=[],
                boot_devices=[],
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
            ),
        )

        rest_client.get_record.side_effect = [
            None,
            dict(
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="XLAB-test-tag1,XLAB-test-tag2",
                description="desc",
                mem=42,
                state="SHUTDOWN",
                numVCPU=2,
                netDevs=[],
                blockDevs=[],
                bootDevices=[],
                attachGuestToolsISO=False,
                operatingSystem=None,
                affinityStrategy={
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                snapshotScheduleUUID="snapshot-id",
            ),
            dict(
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="XLAB-test-tag1,XLAB-test-tag2",
                description="desc",
                mem=42,
                state="SHUTDOWN",
                numVCPU=2,
                netDevs=[],
                blockDevs=[],
                bootDevices=[],
                attachGuestToolsISO=False,
                operatingSystem=None,
                affinityStrategy={
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                snapshotScheduleUUID="snapshot-id",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        rest_client.create_record.return_value = {
            "taskTag": 123,
            "createdUUID": "",
        }
        result = vm.ensure_present(module, rest_client)
        assert result == (
            True,
            [
                {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "shutdown",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                }
            ],
            {
                "after": {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "shutdown",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                },
                "before": None,
            },
        )

    def test_ensure_present_boot_devices_set_power_state_is_shutdown(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                description="desc",
                memory=42,
                vcpu=2,
                power_state="shutdown",
                state="present",
                tags="",
                disks=[
                    dict(
                        type="virtio_disk",
                        disk_slot=0,
                        size=1000000,
                    ),
                ],
                nics=[],
                boot_devices=[
                    dict(
                        type="virtio_disk",
                        disk_slot=0,
                        size=4200,
                    ),
                ],
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
            ),
        )

        rest_client.get_record.side_effect = [
            None,
            dict(
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="XLAB-test-tag1,XLAB-test-tag2",
                description="desc",
                mem=42,
                state="SHUTDOWN",
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
                    ),
                ],
                bootDevices=[],
                attachGuestToolsISO=False,
                operatingSystem=None,
                affinityStrategy={
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                snapshotScheduleUUID="shapshot-id",
            ),
            dict(
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="XLAB-test-tag1,XLAB-test-tag2",
                description="desc",
                mem=42,
                state="SHUTDOWN",
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
                    ),
                ],
                bootDevices=["id"],
                attachGuestToolsISO=False,
                operatingSystem=None,
                affinityStrategy={
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                snapshotScheduleUUID="shapshot-id",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        rest_client.create_record.return_value = {
            "taskTag": 123,
            "createdUUID": "",
        }

        rest_client.update_record.return_value = {
            "taskTag": 124,
            "createdUUID": "",
        }
        result = vm.ensure_present(module, rest_client)
        assert result == (
            True,
            [
                {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [
                        {
                            "cache_mode": "none",
                            "disable_snapshotting": False,
                            "disk_slot": 0,
                            "iso_name": "jc1-disk-0",
                            "mount_points": [],
                            "read_only": False,
                            "size": 4200,
                            "tiering_priority_factor": 8,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "description": "desc",
                    "disks": [
                        {
                            "cache_mode": "none",
                            "disable_snapshotting": False,
                            "disk_slot": 0,
                            "iso_name": "jc1-disk-0",
                            "mount_points": [],
                            "read_only": False,
                            "size": 4200,
                            "tiering_priority_factor": 8,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "shutdown",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                }
            ],
            {
                "after": {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [
                        {
                            "cache_mode": "none",
                            "disable_snapshotting": False,
                            "disk_slot": 0,
                            "iso_name": "jc1-disk-0",
                            "mount_points": [],
                            "read_only": False,
                            "size": 4200,
                            "tiering_priority_factor": 8,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "description": "desc",
                    "disks": [
                        {
                            "cache_mode": "none",
                            "disable_snapshotting": False,
                            "disk_slot": 0,
                            "iso_name": "jc1-disk-0",
                            "mount_points": [],
                            "read_only": False,
                            "size": 4200,
                            "tiering_priority_factor": 8,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "shutdown",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                },
                "before": None,
            },
        )

    def test_ensure_present_no_boot_devices_set_power_state_is_not_shutdown(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                description="desc",
                memory=42,
                vcpu=2,
                power_state="start",
                state="present",
                tags="",
                disks=[
                    dict(
                        type="virtio_disk",
                        disk_slot=0,
                        size=1000000,
                    ),
                ],
                nics=[],
                boot_devices=[],
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
            ),
        )

        rest_client.get_record.side_effect = [
            None,
            dict(
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="XLAB-test-tag1,XLAB-test-tag2",
                description="desc",
                mem=42,
                state="SHUTDOWN",
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
                    ),
                ],
                bootDevices=[],
                attachGuestToolsISO=False,
                operatingSystem=None,
                affinityStrategy={
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                snapshotScheduleUUID="shapshot-id",
            ),
            dict(
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="XLAB-test-tag1,XLAB-test-tag2",
                description="desc",
                mem=42,
                state="SHUTDOWN",
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
                    ),
                ],
                bootDevices=[],
                attachGuestToolsISO=False,
                operatingSystem=None,
                affinityStrategy={
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                snapshotScheduleUUID="shapshot-id",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        rest_client.create_record.return_value = {
            "taskTag": 123,
            "createdUUID": "",
        }

        rest_client.update_record.return_value = {
            "taskTag": 124,
            "createdUUID": "",
        }
        result = vm.ensure_present(module, rest_client)
        assert result == (
            True,
            [
                {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [
                        {
                            "cache_mode": "none",
                            "disable_snapshotting": False,
                            "disk_slot": 0,
                            "iso_name": "jc1-disk-0",
                            "mount_points": [],
                            "read_only": False,
                            "size": 4200,
                            "tiering_priority_factor": 8,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "shutdown",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                }
            ],
            {
                "after": {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [
                        {
                            "cache_mode": "none",
                            "disable_snapshotting": False,
                            "disk_slot": 0,
                            "iso_name": "jc1-disk-0",
                            "mount_points": [],
                            "read_only": False,
                            "size": 4200,
                            "tiering_priority_factor": 8,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "memory": 42,
                    "nics": [],
                    "node_affinity": {
                        "backup_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "preferred_node": {
                            "backplane_ip": "",
                            "lan_ip": "",
                            "node_uuid": "",
                            "peer_id": None,
                        },
                        "strict_affinity": False,
                    },
                    "operating_system": None,
                    "power_state": "shutdown",
                    "snapshot_schedule": "",
                    "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                },
                "before": None,
            },
        )


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-name-unique",
            description="VM-desc",
            memory=42,
            vcpu=4,
            power_state="start",
            tags=["VM-group", "tag1", "tag2"],
            disks=[
                dict(
                    type="virtio_disk",
                    disk_slot=0,
                    size=100000,
                )
            ],
            nics=[
                dict(
                    vlan=0,
                    type="RTL8139",
                )
            ],
            boot_devices=[
                dict(
                    type="virtio_disk",
                    disk_slot=0,
                )
            ],
            cloud_init=dict(
                user_data=dict(expression1="user-data"),
                meta_data=dict(expression2="meta-data"),
            ),
            state="absent",
        )
        success, result = run_main(vm, params)
        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-name-unique",
            state="absent",
        )
        success, result = run_main(vm, params)
        assert success is True

    def test_fail_no_required_fields(self, run_main):
        success, result = run_main(vm)
        assert success is False
        assert result["msg"] == "missing required arguments: state, vm_name"

    def test_fail_required_if(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-name-unique",
            state="present",
        )
        success, result = run_main(vm, params)
        assert success is False
        expected_fail_msg = "state is present but all of the following are missing: memory, vcpu, disks, nics"
        assert result["msg"] == expected_fail_msg
