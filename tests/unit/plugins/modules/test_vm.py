from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm

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
                machine_type="BIOS",
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
            machineType="scale-7.2",
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
                    "machine_type": "BIOS",
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
                    "machine_type": "BIOS",
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
            False,
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
                machine_type="BIOS",
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
            machineType="scale-7.2",
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
                    "machine_type": "BIOS",
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
                    "machine_type": "BIOS",
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
            False,
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
                machine_type="BIOS",
            ),
        )
        rest_client.get_record.return_value = None

        result = vm.ensure_absent(module, rest_client)

        assert result == (False, [], dict(), False)


class TestEnsurePresent:
    def test_ensure_present_create_record(
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
                vm_name_new=None,
                description="description",
                memory=42000,
                vcpu=3,
                power_state="shutdown",
                state="present",
                tags=["group"],
                disks=[],
                nics=[],
                boot_devices=[],
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
                machine_type="BIOS",
            ),
        )

        rest_client.get_record.side_effect = [
            None,  # vm_before does not exist
            dict(  # vm_created
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="group",
                description="description",
                mem=42000,
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
                machineType="scale-7.2",
            ),
            dict(  # vm_after
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="group",
                description="description",
                mem=42000,
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
                machineType="scale-7.2",
            ),
        ]

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None  # in VM.get_by_name
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None  # in VM.get_by_name
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.post_vm_payload"
        )  # we don't need to generate payload since we also mock create record
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.ManageVMParams.set_vm_params"
        ).return_value = (True, True, dict())
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
                    "description": "description",
                    "disks": [],
                    "machine_type": "BIOS",
                    "memory": 42000,
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
                    "tags": ["group"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                }
            ],
            {
                "after": {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "description",
                    "disks": [],
                    "machine_type": "BIOS",
                    "memory": 42000,
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
                    "tags": ["group"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                },
                "before": None,
            },
            False,
        )

    def test_ensure_present_update_record_manage_vm_params(
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
                vm_name_new="VM-name-updated",
                description="desc-updated",
                memory=42000,
                vcpu=3,
                power_state="shutdown",
                state="present",
                tags=["group"],
                disks=[],
                nics=[],
                boot_devices=[],
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
                machine_type="BIOS",
            ),
        )

        rest_client.get_record.side_effect = [  # in VM.get_by_name
            dict(  # vm_before
                uuid="id",
                nodeUUID="",
                name="VM-name-unique",
                tags="",
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
                machineType="scale-7.2",
            ),
            dict(  # vm_after
                uuid="id",
                nodeUUID="",
                name="VM-name-updated",
                tags="group",
                description="desc-updated",
                mem=42000,
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
                machineType="scale-7.2",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None  # in VM.get_by_name
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None  # in VM.get_by_name
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_vm_params"
        ).return_value = (True, True)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_disks"
        ).return_value = (True, True)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_nics"
        ).return_value = (True, True)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_boot_order"
        ).return_value = (False, False)

        result = vm.ensure_present(module, rest_client)
        assert result == (
            True,
            [
                {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc-updated",
                    "disks": [],
                    "machine_type": "BIOS",
                    "memory": 42000,
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
                    "tags": ["group"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-updated",
                }
            ],
            {
                "after": {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc-updated",
                    "disks": [],
                    "machine_type": "BIOS",
                    "memory": 42000,
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
                    "tags": ["group"],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-updated",
                },
                "before": {
                    "attach_guest_tools_iso": False,
                    "boot_devices": [],
                    "description": "desc",
                    "disks": [],
                    "machine_type": "BIOS",
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
                    "tags": [""],
                    "uuid": "id",
                    "vcpu": 2,
                    "vm_name": "VM-name-unique",
                },
            },
            False,
        )

    def test_ensure_present_update_record_no_changes(
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
                vm_name_new="VM-name-updated",
                description="desc-updated",
                memory=42000,
                vcpu=3,
                power_state="shutdown",
                state="present",
                tags=["group"],
                disks=[],
                nics=[],
                boot_devices=[],
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
                machine_type="BIOS",
            ),
        )

        rest_client.get_record.side_effect = [
            dict(
                uuid="id",
                nodeUUID="",
                name="VM-name-updated",
                tags="group",
                description="desc-updated",
                mem=42000,
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
                machineType="scale-7.2",
            ),
            dict(
                uuid="id",
                nodeUUID="",
                name="VM-name-updated",
                tags="group",
                description="desc-updated",
                mem=42000,
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
                machineType="scale-7.2",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_vm_params"
        ).return_value = (False, False)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_disks"
        ).return_value = (False, False)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_boot_order"
        ).return_value = (False, False)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_nics"
        ).return_value = (False, False)

        result = vm.ensure_present(module, rest_client)
        changed = result[0]
        assert not changed

    def test_ensure_present_updated_boot_order(
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
                boot_devices=[
                    dict(
                        type="virtio_disk",
                        disk_slot=0,
                        size=1000000,
                    ),
                ],
                attach_guest_tools_iso=None,
                cloud_init=dict(
                    user_data=None,
                    meta_data=None,
                ),
                vm_name_new=None,
                machine_type="BIOS",
            ),
        )

        rest_client.get_record.side_effect = [
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
                machineType="scale-7.2",
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
                machineType="scale-7.2",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_vm_params"
        ).return_value = (False, False)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_disks"
        ).return_value = (True, True)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_boot_order"
        ).return_value = (True, True)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm._set_nics"
        ).return_value = (False, False)

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
                            "tiering_priority_factor": 4,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "machine_type": "BIOS",
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
                            "tiering_priority_factor": 4,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "machine_type": "BIOS",
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
                "before": {
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
                            "tiering_priority_factor": 4,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "machine_type": "BIOS",
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
            True,
        )

    def test_ensure_present_create_vm_no_boot_devices_power_state_is_shutdown(
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
                machine_type="BIOS",
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
                machineType="scale-7.2",
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
                machineType="scale-7.2",
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
                    "machine_type": "BIOS",
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
                    "machine_type": "BIOS",
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
            False,
        )

    def test_ensure_present_create_vm_boot_devices_set_power_state_is_shutdown(
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
                machine_type="BIOS",
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
                machineType="scale-7.2",
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
                machineType="scale-7.2",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.wait_shutdown"
        ).return_value = True
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
                            "tiering_priority_factor": 4,
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
                            "tiering_priority_factor": 4,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "machine_type": "BIOS",
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
                            "tiering_priority_factor": 4,
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
                            "tiering_priority_factor": 4,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "machine_type": "BIOS",
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
            False,
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
                machine_type="BIOS",
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
                machineType="scale-7.2",
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
                machineType="scale-7.2",
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
                            "tiering_priority_factor": 4,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "machine_type": "BIOS",
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
                            "tiering_priority_factor": 4,
                            "type": "virtio_disk",
                            "uuid": "id",
                            "vm_uuid": "vm-id",
                        }
                    ],
                    "machine_type": "BIOS",
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
            False,
        )


class TestMain:
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
