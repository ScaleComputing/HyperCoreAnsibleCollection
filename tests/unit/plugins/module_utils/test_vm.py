from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import (
    VM,
    ManageVMParams,
    ManageVMDisks,
    ManageVMNics,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.errors import (
    ScaleComputingError,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.disk import Disk
from ansible_collections.scale_computing.hypercore.plugins.module_utils.nic import Nic
from ansible_collections.scale_computing.hypercore.plugins.module_utils.iso import ISO
from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.snapshot_schedule import (
    SnapshotSchedule,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestVM:
    def test_vm_from_ansible(self):
        vm_dict = dict(
            uuid=None,  # No uuid when creating object from ansible
            vm_name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="running",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system=None,
        )

        vm = VM(
            uuid=None,
            name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="running",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system=None,
        )

        vm_from_ansible = VM.from_ansible(vm_dict)
        assert vm == vm_from_ansible

    def test_vm_from_hypercore_dict_is_not_none(self, rest_client, mocker):
        vm = VM(
            uuid="",  # No uuid when creating object from ansible
            node_uuid="412a3e85-8c21-4138-a36e-789eae3548a3",
            name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="started",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=[],
            attach_guest_tools_iso=False,
            operating_system=None,
            node_affinity={
                "strict_affinity": False,
                "preferred_node": dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                ),
                "backup_node": dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                ),
            },
            snapshot_schedule="",
        )

        vm_dict = dict(
            uuid="",
            nodeUUID="412a3e85-8c21-4138-a36e-789eae3548a3",
            name="VM-name",
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
            snapshotScheduleUUID="9238175f-2d6a-489f-9157-fa6345719b3b",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None

        vm_from_hypercore = VM.from_hypercore(vm_dict, rest_client)
        assert vm == vm_from_hypercore

    def test_vm_from_hypercore_dict_is_none(self, rest_client):
        vm = None
        vm_dict = None
        vm_from_hypercore = VM.from_hypercore(vm_dict, rest_client)
        assert vm == vm_from_hypercore

    def test_vm_to_hypercore(self):
        vm = VM(
            uuid=None,  # No uuid when creating object from ansible
            name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="start",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system="os_windows_server_2012",
        )

        assert vm.to_hypercore() == dict(
            name="VM-name",
            description="desc",
            mem=42,
            numVCPU=2,
            blockDevs=[],
            netDevs=[],
            bootDevices=[],
            tags="XLAB-test-tag1,XLAB-test-tag2",
            uuid=None,
            attachGuestToolsISO=False,
            operatingSystem="os_windows_server_2012",
            state="START",
        )

    def test_vm_to_ansible(self):
        vm = VM(
            uuid=None,  # No uuid when creating object from ansible
            name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="running",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system="os_windows_server_2012",
            node_affinity={
                "strict_affinity": True,
                "preferred_node": {
                    "node_uuid": "412a3e85-8c21-4138-a36e-789eae3548a3",
                    "backplane_ip": "10.0.0.1",
                    "lan_ip": "10.0.0.2",
                    "peer_id": 1,
                },
                "backup_node": {
                    "node_uuid": "f6v3c6b3-99c6-475b-8e8e-9ae2587db5fc",
                    "backplane_ip": "10.0.0.3",
                    "lan_ip": "10.0.0.4",
                    "peer_id": 2,
                },
            },
        )

        assert vm.to_ansible() == dict(
            uuid=None,  # No uuid when creating object from ansible
            vm_name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="running",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=[],
            attach_guest_tools_iso=False,
            operating_system="os_windows_server_2012",
            node_affinity={
                "strict_affinity": True,
                "preferred_node": {
                    "node_uuid": "412a3e85-8c21-4138-a36e-789eae3548a3",
                    "backplane_ip": "10.0.0.1",
                    "lan_ip": "10.0.0.2",
                    "peer_id": 1,
                },
                "backup_node": {
                    "node_uuid": "f6v3c6b3-99c6-475b-8e8e-9ae2587db5fc",
                    "backplane_ip": "10.0.0.3",
                    "lan_ip": "10.0.0.4",
                    "peer_id": 2,
                },
            },
            snapshot_schedule=None,
        )

    def test_find_disk(self):
        # TODO (domen): Write tests for find_disk, if necessary
        pass

    def test_equal_true(self):
        assert VM(
            uuid=None,  # No uuid when creating object from ansible
            node_uuid="412a3e85-8c21-4138-a36e-789eae3548a3",
            name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="started",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system="os_windows_server_2012",
            node_affinity={
                "strict_affinity": True,
                "preferred_node": {
                    "node_uuid": "412a3e85-8c21-4138-a36e-789eae3548a3",
                    "backplane_ip": "10.0.0.1",
                    "lan_ip": "10.0.0.2",
                    "peer_id": 1,
                },
                "backup_node": {
                    "node_uuid": "f6v3c6b3-99c6-475b-8e8e-9ae2587db5fc",
                    "backplane_ip": "10.0.0.3",
                    "lan_ip": "10.0.0.4",
                    "peer_id": 2,
                },
            },
        ) == VM(
            uuid=None,  # No uuid when creating object from ansible
            node_uuid="412a3e85-8c21-4138-a36e-789eae3548a3",
            name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="started",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system="os_windows_server_2012",
            node_affinity={
                "strict_affinity": True,
                "preferred_node": {
                    "node_uuid": "412a3e85-8c21-4138-a36e-789eae3548a3",
                    "backplane_ip": "10.0.0.1",
                    "lan_ip": "10.0.0.2",
                    "peer_id": 1,
                },
                "backup_node": {
                    "node_uuid": "f6v3c6b3-99c6-475b-8e8e-9ae2587db5fc",
                    "backplane_ip": "10.0.0.3",
                    "lan_ip": "10.0.0.4",
                    "peer_id": 2,
                },
            },
        )

    def test_equal_false(self):
        assert VM(
            uuid=None,  # No uuid when creating object from ansible
            name="VM-name",
            node_uuid="412a3e85-8c21-4138-a36e-789eae3548a3",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="started",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system="os_windows_server_2012",
            node_affinity={},
        ) != VM(
            uuid=None,  # No uuid when creating object from ansible
            name="VM   NAME    CHANGED !!!!!!",
            node_uuid="412a3e85-8c21-4138-a36e-789eae3548a3",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="started",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system="os_windows_server_2012",
            node_affinity={},
        )

    def test_get_by_name(self, rest_client, mocker):
        ansible_dict = dict(
            vm_name="vm-name",
        )
        rest_client.get_record.return_value = dict(
            uuid="id",
            nodeUUID="node_id",
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
            snapshotScheduleUUID="snapshot_schedule_id",
        )

        vm = VM(
            attach_guest_tools_iso=False,
            boot_devices=[],
            description="desc",
            disks=[],
            memory=42,
            name="VM-name-unique",
            nics=[],
            vcpu=2,
            operating_system=None,
            power_state="started",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            uuid="id",
            node_uuid="node_id",
            node_affinity={
                "strict_affinity": False,
                "preferred_node": dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                ),
                "backup_node": dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                ),
            },
            snapshot_schedule="",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        vm_by_name = VM.get_by_name(ansible_dict, rest_client)
        assert vm == vm_by_name

    def test_get_specific_disk_result_not_empty(self):
        vm = VM(
            attach_guest_tools_iso=False,
            boot_devices=[],
            description="desc",
            disks=[
                Disk(
                    type="virtio_disk",
                    slot=0,
                    cache_mode="none",
                    size=4200,
                    uuid="id",
                    name="jc1-disk-0",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    mount_points=[],
                    read_only=False,
                ),
                Disk(
                    type="ide_cdrom",
                    slot=1,
                    cache_mode="none",
                    size=4200,
                    uuid="id",
                    name="jc1-disk-0",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    mount_points=[],
                    read_only=False,
                ),
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

        disk_query = dict(type="virtio_disk", disk_slot=0)
        specific_disk = vm.get_specific_disk(disk_query)
        assert specific_disk == dict(
            type="virtio_disk",
            disk_slot=0,
            size=4200,
            uuid="id",
            vm_uuid=None,
            cache_mode="none",
            iso_name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=8,
            mount_points=[],
            read_only=False,
        )

    def test_get_specific_disk_result_empty(self):
        vm = VM(
            attach_guest_tools_iso=False,
            boot_devices=[],
            description="desc",
            disks=[
                Disk(
                    type="virtio_disk",
                    slot=1,
                    cache_mode="none",
                    size=4200,
                    uuid="id",
                    name="jc1-disk-0",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    mount_points=[],
                    read_only=False,
                ),
                Disk(
                    type="ide_cdrom",
                    slot=1,
                    cache_mode="none",
                    size=4200,
                    uuid="id",
                    name="jc1-disk-0",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    mount_points=[],
                    read_only=False,
                ),
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

        disk_query = dict(type="virtio_disk", disk_slot=0)
        assert vm.get_specific_disk(disk_query) is None

    def test_get_specific_disk_multiple_results(self):
        vm = VM(
            attach_guest_tools_iso=False,
            boot_devices=[],
            description="desc",
            disks=[
                Disk(
                    type="virtio_disk",
                    slot=0,
                    cache_mode="none",
                    size=4200,
                    uuid="id",
                    name="jc1-disk-0",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    mount_points=[],
                    read_only=False,
                ),
                Disk(
                    type="virtio_disk",
                    slot=0,
                    cache_mode="none",
                    size=4200,
                    uuid="id",
                    name="jc1-disk-0",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    mount_points=[],
                    read_only=False,
                ),
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

        disk_query = dict(type="virtio_disk", disk_slot=0)
        with pytest.raises(errors.ScaleComputingError, match="Disk"):
            vm.get_specific_disk(disk_query)

    def test_get_or_fail_when_get(self, rest_client, mocker):
        rest_client.list_records.return_value = [
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "nodeUUID": "",
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
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                "snapshotScheduleUUID": "snapshot_schedule_id",
            }
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        hypercore_dict = rest_client.list_records.return_value[0]
        actual = VM.from_hypercore(
            vm_dict=hypercore_dict, rest_client=rest_client
        ).to_hypercore()
        results = VM.get_or_fail(
            query={"name": "XLAB_test_vm"}, rest_client=rest_client
        )[0].to_hypercore()
        assert results == actual

    def test_get_or_fail_when_fail(self, rest_client):
        rest_client.list_records.return_value = []
        with pytest.raises(
            errors.VMNotFound,
            match="Virtual machine - {'name': 'XLAB-test-vm'} - not found",
        ):
            VM.get_or_fail(query={"name": "XLAB-test-vm"}, rest_client=rest_client)

    def test_post_vm_payload_cloud_init_absent(self, rest_client):
        vm = VM(
            uuid=None,
            name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="started",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=[],
            attach_guest_tools_iso=False,
            operating_system=None,
        )

        post_vm_payload = vm.post_vm_payload(rest_client, {})

        assert post_vm_payload == {
            "dom": {
                "blockDevs": [
                    {
                        "cacheMode": "WRITETHROUGH",
                        "capacity": 0,
                        "path": "",
                        "type": "IDE_CDROM",
                        "uuid": "cdrom",
                    }
                ],
                "bootDevices": [],
                "description": "desc",
                "machineType": "scale-7.2",
                "mem": 42,
                "name": "VM-name",
                "netDevs": [],
                "numVCPU": 2,
                "tags": "XLAB-test-tag1,XLAB-test-tag2",
            },
            "options": {"attachGuestToolsISO": False},
        }

    def test_post_vm_payload_cloud_init_present(self, rest_client):
        vm = VM(
            uuid=None,
            name="VM-name",
            tags=["XLAB-test-tag1", "XLAB-test-tag2"],
            description="desc",
            memory=42,
            power_state="started",
            vcpu=2,
            nics=[],
            disks=[],
            boot_devices=[],
            attach_guest_tools_iso=False,
            operating_system=None,
        )

        ansible_dict = dict(
            cloud_init=dict(
                user_data="cloud_init-user-data",
                meta_data="cloud_init-meta-data",
            )
        )

        post_vm_payload = vm.post_vm_payload(rest_client, ansible_dict)

        assert post_vm_payload == {
            "dom": {
                "CloudIinitData": {
                    "metaData": "Y2xvdWRfaW5pdC1tZXRhLWRhdGE=",
                    "userData": "Y2xvdWRfaW5pdC11c2VyLWRhdGE=",
                },
                "blockDevs": [
                    {
                        "cacheMode": "WRITETHROUGH",
                        "capacity": 0,
                        "path": "",
                        "type": "IDE_CDROM",
                        "uuid": "cdrom",
                    }
                ],
                "bootDevices": [],
                "description": "desc",
                "machineType": "scale-7.2",
                "mem": 42,
                "name": "VM-name",
                "netDevs": [],
                "numVCPU": 2,
                "tags": "XLAB-test-tag1,XLAB-test-tag2",
            },
            "options": {"attachGuestToolsISO": False},
        }

    def test_post_vm_payload_set_disks(self, rest_client):
        vm_dict = dict(
            uuid="",
            nodeUUID="412a3e85-8c21-4138-a36e-789eae3548a3",
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
                    name="VIRTIO_DISK",
                    disableSnapshotting=False,
                    tieringPriorityFactor=8,
                    mountPoints=[],
                    readOnly=False,
                )
            ],
            bootDevices=[],
            attachGuestToolsISO=False,
            operatingSystem=None,
            affinityStrategy={
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
        )

        VM._post_vm_payload_set_disks(vm_dict, rest_client)

        assert vm_dict == {
            "affinityStrategy": {
                "backupNodeUUID": "",
                "preferredNodeUUID": "",
                "strictAffinity": False,
            },
            "attachGuestToolsISO": False,
            "blockDevs": [
                {
                    "cacheMode": "WRITETHROUGH",
                    "capacity": 0,
                    "path": "",
                    "type": "IDE_CDROM",
                    "uuid": "cdrom",
                },
                {
                    "cacheMode": "NONE",
                    "capacity": 4200,
                    "type": "VIRTIO_DISK",
                    "uuid": "primaryDrive",
                },
            ],
            "bootDevices": [],
            "description": "desc",
            "mem": 42,
            "name": "VM-name",
            "netDevs": [],
            "nodeUUID": "412a3e85-8c21-4138-a36e-789eae3548a3",
            "numVCPU": 2,
            "operatingSystem": None,
            "state": "RUNNING",
            "tags": "XLAB-test-tag1,XLAB-test-tag2",
            "uuid": "",
        }

    def test_update_boot_device_order(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="VM-name",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        vm = VM.from_hypercore(
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "nodeUUID": "",
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
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                "snapshotScheduleUUID": "",
            },
            rest_client,
        )
        boot_order = ["device1-id", "device2-id"]
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "createdUUID": "disk-id",
        }
        VM.update_boot_device_order(module, rest_client, vm, boot_order)
        rest_client.update_record.assert_called_with(
            "/rest/v1/VirDomain/7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            dict(
                bootDevices=["device1-id", "device2-id"],
                uuid="7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            ),
            False,
        )


class TestNic:
    @classmethod
    def _get_test_vm(cls, rest_client, mocker):
        nic_dict_1 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "macAddress": "12-34-56-78-AB",
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "connected": True,
        }
        nic_dict_2 = {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "RTL8139",
            "vlan_new": 1,
            "macAddress": "12-34-56-78-CD",
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "connected": True,
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        return VM.from_hypercore(
            {
                "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "nodeUUID": "",
                "name": "XLAB_test_vm",
                "blockDevs": [],
                "netDevs": [nic_dict_1, nic_dict_2],
                "stats": "bla",
                "tags": "XLAB,test",
                "description": "test vm",
                "mem": 23424234,
                "state": "RUNNING",
                "numVCPU": 2,
                "bootDevices": [],
                "operatingSystem": "windows",
                "affinityStrategy": {
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                "snapshotScheduleUUID": "",
            },
            rest_client,
        )

    def test_delete_unused_nics_to_hypercore_vm_when_no_delete(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
            )
        )
        vm_dict = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
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
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        rest_client.list_records.return_value = [vm_dict]
        virtual_machine = VM.get(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )[0]
        nic_key = "items"
        results = virtual_machine.delete_unused_nics_to_hypercore_vm(
            module, rest_client, nic_key
        )
        assert results == (False, False)

    def test_delete_unused_nics_to_hypercore_vm_when_one_nic_deleted(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
            )
        )
        nic_dict = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "macAddress": "12-34-56-78-CD",
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "connected": True,
        }
        vm_dict = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [nic_dict],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        rest_client.list_records.return_value = [vm_dict]
        rest_client.delete_record.return_value = {"taskTag": "1234"}
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        virtual_machine = VM.get(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )[0]
        nic_key = "items"
        results = virtual_machine.delete_unused_nics_to_hypercore_vm(
            module, rest_client, nic_key
        )
        assert results == (True, False)

    def test_delete_unused_nics_to_hypercore_vm_when_multiple_nic_deleted(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
            )
        )
        nic_dict_1 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        nic_dict_2 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "virtio",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        vm_dict = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [nic_dict_1, nic_dict_2],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        rest_client.list_records.return_value = [vm_dict]
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        rest_client.delete_record.side_effect = [
            {"taskTag": "1234"},
            {"taskTag": "5678"},
        ]
        virtual_machine = VM.get(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )[0]
        nic_key = "items"
        results = virtual_machine.delete_unused_nics_to_hypercore_vm(
            module, rest_client, nic_key
        )
        assert results == (True, False)

    def test_find_nic_vlan(self, rest_client, mocker):
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        virtual_machine = self._get_test_vm(rest_client, mocker)
        results = virtual_machine.find_nic(vlan=1)
        assert results[1] is (None)
        assert results[0].vlan == 1
        assert results[0].mac == "12-34-56-78-AB"
        assert results[0].uuid == "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"
        assert results[0].vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        assert results[0].connected is True

    def test_find_nic_vlan_and_vlan_new(self, rest_client, mocker):
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        virtual_machine = self._get_test_vm(rest_client, mocker)
        results = virtual_machine.find_nic(vlan=2, vlan_new=1)
        assert results[0].vlan == 2
        assert results[0].mac == "12-34-56-78-CD"
        assert results[0].uuid == "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"
        assert results[0].vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        assert results[0].connected is True
        assert results[1].vlan == 1
        assert results[1].mac == "12-34-56-78-AB"
        assert results[1].uuid == "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"
        assert results[1].vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        assert results[1].connected is True

    def test_find_nic_mac(self, rest_client, mocker):
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        virtual_machine = self._get_test_vm(rest_client, mocker)
        results = virtual_machine.find_nic(mac="12-34-56-78-CD")
        print(results)
        assert results[0].vlan == 2
        assert results[0].mac == "12-34-56-78-CD"
        assert results[0].uuid == "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"
        assert results[0].vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        assert results[0].connected is True

    def test_find_nic_mac_and_mac_new(self, rest_client, mocker):
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        virtual_machine = self._get_test_vm(rest_client, mocker)
        results = virtual_machine.find_nic(
            mac="12-34-56-78-CD", mac_new="12-34-56-78-AB"
        )
        print(results)
        assert results[0].vlan == 2
        assert results[0].mac == "12-34-56-78-CD"
        assert results[0].uuid == "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"
        assert results[0].vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        assert results[0].connected is True
        assert results[1].vlan == 1
        assert results[1].mac == "12-34-56-78-AB"
        assert results[1].uuid == "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"
        assert results[1].vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        assert results[1].connected is True


class TestVMExport:
    def test_create_export_or_import_vm_payload_when_export(self):
        ansible_dict = {
            "vm_name": "this-vm-name",
            "smb": {
                "path": "/user",
                "username": "username",
                "password": "password",
                "server": "10.5.11.170",
                "file_name": "my_file.xml",
            },
        }
        results = VM.create_export_or_import_vm_payload(ansible_dict, None, True)
        print(results)
        assert results == dict(
            target=dict(
                pathURI="smb://"
                + "username"
                + ":"
                + "password"
                + "@"
                + "10.5.11.170"
                + "/user",
                definitionFileName="my_file.xml",
            ),
            template=dict(),
        )

    def test_export_vm(self, rest_client, mocker):
        ansible_dict = {
            "vm_name": "this-vm",
            "smb": {
                "server": "smb-server",
                "path": "/somewhere",
                "username": "user",
                "password": "pass",
                "file_name": None,
            },
        }
        smb_dict = {
            "uuid": "8145f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB_test_smb",
            "blockDevs": [],
            "netDevs": [
                {
                    "vlan": 1,
                    "type": "VIRTIO",
                    "ipv4Addresses": ["10.5.11.170"],
                    "virDomainUUID": "8145f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                    "macAddress": "",
                    "connected": True,
                    "uuid": "nic-uuid",
                }
            ],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_id",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        virtual_machine = VM.from_hypercore(smb_dict, rest_client)
        rest_client.list_records.return_value = [smb_dict]
        rest_client.create_record.return_value = {"taskTag": "12345"}
        results = virtual_machine.export_vm(rest_client, ansible_dict)
        assert results == {"taskTag": "12345"}


class TestVMImport:
    def test_create_export_or_import_vm_payload_when_import(self):
        ansible_dict = {
            "vm_name": "this-vm-name",
            "smb": {
                "path": "/user",
                "username": "username",
                "password": "password",
                "server": "10.5.11.170",
                "file_name": "my_file.xml",
            },
        }
        results = VM.create_export_or_import_vm_payload(ansible_dict, None, False)
        print(results)
        assert results == dict(
            source=dict(
                pathURI="smb://"
                + "username"
                + ":"
                + "password"
                + "@"
                + "10.5.11.170"
                + "/user",
                definitionFileName="my_file.xml",
            ),
            template=dict(name="this-vm-name"),
        )

    def test_import_vm(self, rest_client, mocker):
        ansible_dict = {
            "vm_name": "this-vm",
            "smb": {
                "server": "smb-server",
                "path": "/somewhere",
                "username": "user",
                "password": "pass",
                "file_name": None,
            },
        }
        smb_dict = {
            "uuid": "8145f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB_test_smb",
            "blockDevs": [],
            "netDevs": [
                {
                    "vlan": 1,
                    "type": "VIRTIO",
                    "ipv4Addresses": ["10.5.11.170"],
                    "virDomainUUID": "8145f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                    "macAddress": "",
                    "connected": True,
                    "uuid": "nic-uuid",
                }
            ],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_id",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        virtual_machine = VM.from_hypercore(smb_dict, rest_client)
        rest_client.list_records.return_value = [smb_dict]
        rest_client.create_record.return_value = {"taskTag": "12345"}
        results = virtual_machine.import_vm(rest_client, ansible_dict)
        assert results == {"taskTag": "12345"}

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

        source_object_ansible = vm.get_vm_device(desired_source_object)

        assert source_object_ansible == {
            "cache_mode": "none",
            "disable_snapshotting": False,
            "disk_slot": 0,
            "mount_points": [],
            "iso_name": "jc1-disk-0",
            "read_only": False,
            "size": 4200,
            "tiering_priority_factor": 8,
            "type": "virtio_disk",
            "uuid": "id",
            "vm_uuid": "vm-id",
        }


class TestVMClone:
    def test_create_clone_vm_payload_without_cloud_init(self):
        results = VM.create_clone_vm_payload(
            "clone_name", ["bla", "bla1"], ["oroginal_tag", "original_tag2"], None
        )
        print(results)
        assert results == {
            "template": {
                "name": "clone_name",
                "tags": "oroginal_tag,original_tag2,bla,bla1",
            }
        }

    def test_create_clone_vm_payload_with_cloud_init(self):
        results = VM.create_clone_vm_payload(
            "clone_name",
            ["bla", "bla1"],
            ["oroginal_tag", "original_tag2"],
            {"userData": "something", "metaData": "else"},
        )
        print(results)
        assert results == {
            "template": {
                "name": "clone_name",
                "tags": "oroginal_tag,original_tag2,bla,bla1",
                "cloudInitData": {"userData": "something", "metaData": "else"},
            }
        }

    def test_clone_vm(self, rest_client, mocker):
        ansible_dict = {"vm_name": "XLAB-test-vm-clone", "tags": None}
        vm_dict = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB-test-vm-clone",
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
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_id",
        }
        rest_client.list_records.return_value = [vm_dict]
        rest_client.create_record.return_value = {"taskTag": "1234"}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        virtual_machine = VM.get_or_fail(
            query={"name": "XLAB-test-vm-clone"}, rest_client=rest_client
        )[0]
        results = virtual_machine.clone_vm(rest_client, ansible_dict)
        assert results == {"taskTag": "1234"}


class TestManageVMParams:
    def test_build_payload_empty_strings(self, rest_client, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="VM-unique-name",
                vm_name_new="VM-unique-name-updated",
                description="",
                tags="",
                memory=512,
                vcpu=2,
                power_state="start",
                snapshot_schedule="",
            ),
        )

        payload = ManageVMParams._build_payload(module, rest_client)

        assert payload == {
            "name": "VM-unique-name-updated",
            "description": "",
            "tags": "",
            "mem": 512,
            "numVCPU": 2,
            "snapshotScheduleUUID": "",
        }

    def test_build_payload(self, rest_client, create_module, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="VM-unique-name",
                vm_name_new="VM-unique-name-updated",
                description="Updated parameters",
                tags=["Xlab"],
                memory=512,
                vcpu=2,
                power_state="start",
                snapshot_schedule="snapshot_schedule",
            ),
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = SnapshotSchedule(
            name="snapshot_schedule",
            uuid="snapshot_schedule_uuid",
            recurrences=None,
        )

        payload = ManageVMParams._build_payload(module, rest_client)

        assert payload == {
            "name": "VM-unique-name-updated",
            "description": "Updated parameters",
            "tags": "Xlab",
            "mem": 512,
            "numVCPU": 2,
            "snapshotScheduleUUID": "snapshot_schedule_uuid",
        }

    def test_to_be_changed(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new="new_name",
                description="Updated parameters",
                tags=["Xlab"],
                memory=512,
                vcpu=3,
                power_state="start",
                snapshot_schedule="snapshot_schedule",
            ),
        )

        vm = VM(
            name="old_name",
            vcpu=2,
            memory=512,
            snapshot_schedule="snapshot_schedule",
            power_state="started",
        )

        changed, changed_parameters = ManageVMParams._to_be_changed(vm, module)
        assert changed is True
        assert changed_parameters == {
            "vm_name": True,
            "description": True,
            "tags": True,
            "memory": False,
            "vcpu": True,
            "power_state": False,
            "snapshot_schedule": False,
        }

    def test_to_be_changed_empty_string(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new="new_name",
                description="",
                tags=[],
                memory=512,
                vcpu=3,
                power_state="start",
                snapshot_schedule="",
            ),
        )

        vm = VM(
            name="old_name",
            vcpu=2,
            memory=512,
            snapshot_schedule="snapshot_schedule",
            power_state="started",
        )

        changed, changed_parameters = ManageVMParams._to_be_changed(vm, module)
        assert changed is True
        assert changed_parameters == {
            "vm_name": True,
            "description": True,
            "tags": True,
            "memory": False,
            "vcpu": True,
            "power_state": False,
            "snapshot_schedule": True,
        }

    def test_to_be_changed_empty_string_no_change(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new=None,
                description="",
                tags=[""],
                memory=512,
                vcpu=3,
                power_state="start",
                snapshot_schedule="",
            ),
        )

        vm = VM(
            name="old_name",
            description="",
            vcpu=3,
            memory=512,
            tags=[""],
            snapshot_schedule="",
            power_state="started",
        )

        changed, changed_parameters = ManageVMParams._to_be_changed(vm, module)
        assert changed is False
        assert changed_parameters == {
            "description": False,
            "tags": False,
            "memory": False,
            "vcpu": False,
            "power_state": False,
            "snapshot_schedule": False,
        }

    def test_needs_reboot(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new="new_name",
                description="Updated parameters",
                tags=["Xlab"],
                memory=512000,
                vcpu=2,
                power_state="start",
                snapshot_schedule="snapshot_schedule",
            ),
        )
        changed = {
            "vm_name": True,
            "description": True,
            "tags": True,
            "memory": False,
            "vcpu": True,
            "power_state": True,
            "snapshot_schedule": False,
        }
        reboot_needed = ManageVMParams._needs_reboot(module, changed)

        assert reboot_needed is True

    def test_doesnt_need_reboot(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new="new_name",
                description="Updated parameters",
                tags=["Xlab"],
                power_state="start",
            ),
        )
        changed = {
            "vm_name": True,
            "description": True,
            "tags": True,
            "power_state": True,
        }
        reboot_needed = ManageVMParams._needs_reboot(module, changed)

        assert reboot_needed is False

    def test_build_after_diff(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new="new_name",
                description="Updated description",
                tags=["Xlab", "updated"],
                memory=512000,
                vcpu=4,
                power_state="stop",
                snapshot_schedule="snapshot_schedule_new",
            ),
            check_mode=False,
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_params.VM.get_or_fail"
        ).return_value = [
            VM(
                uuid="vm_uuid",
                node_uuid="vm_node_uuid",
                name="new_name",
                tags=["Xlab", "updated"],
                description="Updated description",
                memory=512000,
                power_state="stop",
                vcpu=4,
                snapshot_schedule="snapshot_schedule_new",
            ),
        ]

        after = dict(
            vm_name="new_name",
            tags=["Xlab", "updated"],
            description="Updated description",
            memory=512000,
            power_state="stop",
            vcpu=4,
            snapshot_schedule="snapshot_schedule_new",
        )

        assert after == ManageVMParams._build_after_diff(module, rest_client)

    def test_build_after_diff_check_mode(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new="new_name",
                description="Updated description",
                tags=["Xlab", "updated"],
                memory=512000,
                vcpu=4,
                power_state="stop",
                snapshot_schedule="snapshot_schedule_new",
            ),
            check_mode=True,
        )

        after = dict(
            vm_name="new_name",
            tags=["Xlab", "updated"],
            description="Updated description",
            memory=512000,
            power_state="stop",
            vcpu=4,
            snapshot_schedule="snapshot_schedule_new",
        )

        assert after == ManageVMParams._build_after_diff(module, rest_client)

    def test_build_before_diff(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new="new_name",
                description="Updated description",
                tags=["Xlab", "updated"],
                memory=512000,
                vcpu=4,
                power_state="stop",
                snapshot_schedule="snapshot_schedule_new",
            ),
        )

        vm_before = VM(
            uuid="vm_uuid",
            node_uuid="vm_node_uuid",
            name="old_name",
            tags=["Xlab"],
            description="description",
            memory=512,
            power_state="started",
            vcpu=2,
            snapshot_schedule="snapshot_schedule_old",
        )

        before = dict(
            vm_name="old_name",
            tags=["Xlab"],
            description="description",
            memory=512,
            power_state="started",
            vcpu=2,
            snapshot_schedule="snapshot_schedule_old",
        )

        assert before == ManageVMParams._build_before_diff(vm_before, module)

    def test_set_vm_params(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new="new_name",
                description="Updated description",
                tags=["Xlab"],
                memory=512,
                vcpu=4,
                power_state="started",
                snapshot_schedule="",
            ),
            check_mode=False,
        )
        rest_client.update_record.return_value = {"taskTag": "1234"}
        vm_before = VM(
            uuid="vm_uuid",
            node_uuid="vm_node_uuid",
            name="old_name",
            tags=["Xlab"],
            description="description",
            memory=512,
            power_state="started",
            vcpu=2,
            snapshot_schedule="",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.TaskTag.wait_task"
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.get_or_fail"
        ).return_value = [
            VM(
                uuid="vm_uuid",
                node_uuid="vm_node_uuid",
                name="new_name",
                tags=["Xlab"],
                description="Updated description",
                memory=512,
                power_state="started",
                vcpu=4,
                snapshot_schedule="",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        changed, rebooted, diff = ManageVMParams.set_vm_params(
            module, rest_client, vm_before
        )

        assert changed is True
        assert rebooted is False
        assert diff == {
            "before": {
                "vm_name": "old_name",
                "description": "description",
                "tags": ["Xlab"],
                "memory": 512,
                "vcpu": 2,
                "power_state": "started",
                "snapshot_schedule": "",
            },
            "after": {
                "vm_name": "new_name",
                "description": "Updated description",
                "tags": ["Xlab"],
                "memory": 512,
                "vcpu": 4,
                "power_state": "started",
                "snapshot_schedule": "",
            },
        }

    def test_run_no_change(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="old_name",
                vm_name_new=None,
                description="description",
                tags=["Xlab"],
                memory=512,
                vcpu=2,
                power_state="started",
                snapshot_schedule="",
            ),
            check_mode=True,
        )

        vm_before = VM(
            uuid="vm_uuid",
            node_uuid="vm_node_uuid",
            name="old_name",
            tags=["Xlab"],
            description="description",
            memory=512,
            power_state="started",
            vcpu=2,
            snapshot_schedule="",
        )

        changed, reboot_needed, diff = ManageVMParams.set_vm_params(
            module, rest_client, vm_before
        )

        assert changed is False
        assert reboot_needed is False
        assert diff == {
            "before": None,
            "after": None,
        }


class TestManageVMDisks:
    def test_get_vm_by_name_disks_empty(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
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
                bootDevices=[],
                attachGuestToolsISO=False,
                operatingSystem=None,
                affinityStrategy=dict(
                    preferredNodeUUID="",
                    strictAffinity=False,
                    backupNodeUUID="",
                ),
                nodeUUID="node-id",
                snapshotScheduleUUID="snapshot_schedule_id",
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
                preferred_node=dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                ),
                backup_node=dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                ),
            ),
            node_uuid="node-id",
            snapshot_schedule="",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = ManageVMDisks.get_vm_by_name(module, rest_client)
        assert result == (vm, [])

    def test_get_vm_by_name_disks_present(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
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
            bootDevices=[],
            attachGuestToolsISO=False,
            operatingSystem=None,
            affinityStrategy=dict(
                preferredNodeUUID="",
                strictAffinity=False,
                backupNodeUUID="",
            ),
            nodeUUID="node-id",
            snapshotScheduleUUID="snapshot_schedule_id",
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
                preferred_node=dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                ),
                backup_node=dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                ),
            ),
            node_uuid="node-id",
            snapshot_schedule="",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = ManageVMDisks.get_vm_by_name(module, rest_client)
        assert result == (
            vm,
            [
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
        )

    def test_create_block_device(self, create_module, rest_client, vm, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
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
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        result = ManageVMDisks._create_block_device(
            module, rest_client, vm, desired_disk
        )
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

    def test_iso_image_management_attach(self, create_module, rest_client, task_wait):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
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
        result = ManageVMDisks.iso_image_management(
            module, rest_client, iso, uuid, attach
        )
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
                unit_test=True,
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
        result = ManageVMDisks.iso_image_management(
            module, rest_client, iso, uuid, attach
        )
        rest_client.update_record.assert_called_with(
            "/rest/v1/VirDomainBlockDevice/disk_id",
            dict(
                path="",
                name="",
            ),
            False,
        )
        assert result is None

    def test_update_block_device(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
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
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        rest_client.update_record.return_value = {
            "taskTag": "123",
            "state": "COMPLETED",
        }
        vm = VM(name="vm-name", memory=42, vcpu=2, uuid="id")
        result = ManageVMDisks._update_block_device(
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

        assert result is False

    def test_delete_not_used_disks_no_deletion(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, type="virtio_disk")],
                state="present",
                force=False,
            ),
            check_mode=False,
        )

        vm = rest_client.get_record.return_value = {
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
            "snapshotScheduleUUID": "snapshot_schedule_id",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        changed = False
        disk_key = "items"
        changed = ManageVMDisks._delete_not_used_disks(
            module, rest_client, VM.from_hypercore(vm, rest_client), changed, disk_key
        )
        rest_client.delete_record.assert_not_called()
        assert not changed

    def test_delete_not_used_disks_deletion(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=2, type="ide_cdrom")],
                state="present",
                force=False,
            )
        )

        vm = rest_client.get_record.return_value = {
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
            "snapshotScheduleUUID": "snapshot_schedule_id",
        }

        changed = False
        rest_client.delete_record.return_value = {
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
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        disk_key = "items"
        changed = ManageVMDisks._delete_not_used_disks(
            module, rest_client, VM.from_hypercore(vm, rest_client), changed, disk_key
        )
        rest_client.delete_record.assert_called_with(
            "/rest/v1/VirDomainBlockDevice/disk-id",
            False,
        )
        assert changed

    def test_force_remove_all_disks_disks_present(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
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
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        result = ManageVMDisks._force_remove_all_disks(
            module, rest_client, vm, disks_before
        )
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
            False,
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
                unit_test=True,
                vm_name="VM-name",
                items=None,
            )
        )
        vm = "Not important"
        disks_before = "Not important"
        with pytest.raises(ScaleComputingError, match="force"):
            ManageVMDisks._force_remove_all_disks(module, rest_client, vm, disks_before)

    def test_ensure_present_create_new_disk(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, size=356, type="virtio_disk")],
                state="present",
                force=False,
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
                "snapshotScheduleUUID": "snapshot_schedule_id",
            },
        ]
        rest_client.create_record.return_value = {
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
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        module_path = "scale_computing.hypercore.vm_disk"
        results = ManageVMDisks.ensure_present_or_set(module, rest_client, module_path)
        assert results == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": True,
                    "disk_slot": 1,
                    "iso_name": None,
                    "mount_points": None,
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
                        "iso_name": None,
                        "mount_points": None,
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
            False,
        )

    def test_ensure_present_update_test_idempotency(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, size=4200, type="virtio_disk")],
                state="present",
                force=False,
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
                "snapshotScheduleUUID": "snapshot_schedule_id",
            },
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        module_path = "scale_computing.hypercore.vm_disk"
        results = ManageVMDisks.ensure_present_or_set(module, rest_client, module_path)
        assert results == (
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
                "before": [
                    {
                        "cache_mode": "none",
                        "disable_snapshotting": False,
                        "disk_slot": 1,
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
            },
            False,
        )

    def test_ensure_present_update_record(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, size=5000, type="virtio_disk")],
                state="present",
                force=False,
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
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.vm_shutdown_forced"
        ).return_value = True
        module_path = "scale_computing.hypercore.vm_disk"
        results = ManageVMDisks.ensure_present_or_set(module, rest_client, module_path)
        assert results == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 1,
                    "iso_name": "jc1-disk-0",
                    "mount_points": [],
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
                        "iso_name": "jc1-disk-0",
                        "mount_points": [],
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
            },
            False,
        )

    def test_ensure_present_attach_iso_cdrom_existing(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, type="ide_cdrom", iso_name="iso-name")],
                state="present",
                force=False,
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
                "snapshotScheduleUUID": "snapshot_schedule_id",
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
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        module_path = "scale_computing.hypercore.vm_disk"
        results = ManageVMDisks.ensure_present_or_set(module, rest_client, module_path)
        assert results == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 1,
                    "iso_name": "iso-name",
                    "mount_points": [],
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
                        "iso_name": "iso-name",
                        "mount_points": [],
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
                        "iso_name": "",
                        "mount_points": [],
                        "read_only": False,
                        "size": 4200,
                        "tiering_priority_factor": 8,
                        "type": "ide_cdrom",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
            False,
        )

    def test_ensure_present_attach_iso_cdrom_absent(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[dict(disk_slot=1, type="ide_cdrom", iso_name="iso-name")],
                state="present",
                force=False,
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
                "snapshotScheduleUUID": "snapshot_schedule_id",
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
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.do_shutdown_steps"
        ).return_value = None
        module_path = "scale_computing.hypercore.vm_disk"
        results = ManageVMDisks.ensure_present_or_set(module, rest_client, module_path)
        assert results == (
            True,
            [
                {
                    "cache_mode": "none",
                    "disable_snapshotting": False,
                    "disk_slot": 1,
                    "iso_name": "iso-name",
                    "mount_points": [],
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
                        "iso_name": "iso-name",
                        "mount_points": [],
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
            False,
        )

    # ensure_present uses only a subset of code of ensure_set. So not testing ensure set again, setting the created
    # disks to empty list as this is tested in this class in methods above already
    def test_ensure_set_force_remove_disks(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="VM-name",
                items=[],
                state="set",
                force=True,
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
            "snapshotScheduleUUID": "snapshot_schedule_id",
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
        module_path = "scale_computing.hypercore.vm_disk"
        result = ManageVMDisks.ensure_present_or_set(module, rest_client, module_path)
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
                        "iso_name": "iso-name",
                        "mount_points": [],
                        "read_only": False,
                        "size": 5000,
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "id",
                        "vm_uuid": "vm-id",
                    }
                ],
            },
            False,
        )

    def test_ensure_set_remove_unused_disk(
        self, create_module, rest_client, task_wait, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
                force=False,
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
                "snapshotScheduleUUID": "snapshot_schedule_id",
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
            },
        ]
        rest_client.delete_record.return_value = {
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
        module_path = "scale_computing.hypercore.vm_disk"
        result = ManageVMDisks.ensure_present_or_set(module, rest_client, module_path)

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
            },
            False,
        )


class TestManageVMNics:
    def test_init_from_ansible_data(self):
        ansible_data = dict(
            # uuid="my-uuid",  # always missing in ansible data?
            # many other fields can be missing too - more tests
            vlan=10,
            type="virtio",
            mac="12:00:00:00:00:00",
            connected=True,  # ATM ansible module does not allow setting connected flag
            # ipv4Addresses=['10.0.0.10', '10.0.1.10'],
        )
        nic = Nic.from_ansible(ansible_data)
        assert 10 == nic.vlan
        assert "virtio" == nic.type  # TODO fix, use enum
        assert "12:00:00:00:00:00" == nic.mac
        # ATM ansible module does not allow setting connected flag
        assert nic.connected is None
        assert [] == nic.ipv4Addresses

    @classmethod
    def _get_nic_from_hypercore(cls):
        hc3_data = dict(
            uuid="my-nic-uuid",
            virDomainUUID="my-vm-uuid",
            vlan=10,
            type="VIRTIO",
            macAddress="12:00:00:00:00:00",
            connected=True,
            ipv4Addresses=["10.0.0.10", "10.0.1.10"],
            # more fields?
        )
        return Nic.from_hypercore(hc3_data)

    @classmethod
    def _get_nic_1(cls):
        return Nic.from_hypercore(
            {
                "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "type": "virtio",
                "macAddress": "00-00-00-00-00",
                "connected": True,
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )

    @classmethod
    def _get_nic_1_dict(cls):
        return dict(
            uuid="6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            virDomainUUID="7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            vlan=1,
            type="virtio",
            macAddress="00-00-00-00-00",
            connected=True,
            ipv4Addresses=["10.0.0.1", "10.0.0.2"],
        )

    @classmethod
    def _get_nic_1_updated(cls):
        return Nic.from_hypercore(
            {
                "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "type": "INTEL_E1000",
                "macAddress": "00-00-00-00-00",
                "connected": True,
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )

    @classmethod
    def _get_nic_1_updated_dict(cls):
        return {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "INTEL_E1000",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }

    def test_get_by_uuid(self, rest_client):
        nic = dict(
            uuid="my-nic-uuid",
            virDomainUUID="my-vm-uuid",
            vlan=10,
            type="VIRTIO",
            macAddress="12:00:00:00:00:00",
            connected=True,
            ipv4Addresses=["10.0.0.10", "10.0.1.10"],
            # more fields?
        )
        nic_dict = nic
        rest_client.get_record.return_value = nic_dict
        results = ManageVMNics.get_by_uuid(
            rest_client=rest_client, nic_uuid="my-nic-uuid"
        )
        print(results)
        nic_dict = Nic.from_hypercore(nic_dict).to_hypercore()
        assert results.to_hypercore() == nic_dict

    def test_send_update_nic_to_hypercore(self, rest_client, create_module, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
            ),
            check_mode=False,
        )
        existing_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        new_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "INTEL_E1000",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
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
        rest_client.update_record.return_value = {"taskTag": "1234"}
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        rest_client.get_record.side_effect = [
            new_nic,
            {"state": "Done"},
        ]
        results = ManageVMNics.send_update_nic_request_to_hypercore(
            module,
            VM.from_hypercore(self._get_empty_test_vm(), rest_client),
            rest_client=rest_client,
            new_nic=Nic.from_hypercore(new_nic),
            existing_nic=Nic.from_hypercore(existing_nic),
            before=[],
            after=[],
        )
        existing_nic = Nic.from_hypercore(existing_nic)
        new_nic = Nic.from_hypercore(new_nic)
        assert results == (
            True,
            [existing_nic.to_ansible()],
            [new_nic.to_ansible()],
            False,
        )

    def test_update_nic_when_one_nic_updated(self, rest_client, create_module, mocker):
        before = []
        after = []
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
            ),
            check_mode=False,
        )
        new_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "vlan_new": 3,
            "macAddress": "12:34:56:78:AB",
            "connected": True,
            "type": "virtio",
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        existing_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "macAddress": "12:34:56:78:AB",
            "connected": True,
            "type": "virtio",
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        new_nic_obj = Nic.from_hypercore(hypercore_data=new_nic)
        existing_nic_obj = Nic.from_hypercore(hypercore_data=existing_nic)
        new_nic_data = new_nic_obj.to_ansible()
        existing_nic_data = existing_nic_obj.to_ansible()
        rest_client.update_record.return_value = {"taskTag": "1234"}
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        rest_client.get_record.side_effect = [
            new_nic,
            {"taskTag": "1234", "state": "Done"},
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
        before.append(existing_nic_data)
        after.append(new_nic_data)
        changed = True
        results = ManageVMNics.send_update_nic_request_to_hypercore(
            module,
            VM.from_hypercore(self._get_empty_test_vm(), rest_client),
            rest_client,
            new_nic_obj,
            existing_nic_obj,
            before,
            after,
        )
        assert results == (changed, before, after, False)

    def test_send_create_nic_to_hypercore(self, rest_client, create_module, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
            ),
            check_mode=False,
        )
        new_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
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
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "state": "COMPLETED",
        }
        rest_client.get_record.side_effect = [
            new_nic,
            {"state": "Done"},
        ]
        results = ManageVMNics.send_create_nic_request_to_hypercore(
            module,
            VM.from_hypercore(self._get_empty_test_vm(), rest_client),
            rest_client=rest_client,
            new_nic=Nic.from_hypercore(new_nic),
            before=[],
            after=[],
        )
        print(results)
        print((True, [None], [Nic.from_hypercore(new_nic).to_ansible()]))
        assert results == (
            True,
            [None],
            [Nic.from_hypercore(new_nic).to_ansible()],
            False,
        )

    def test_send_delete_nic_request_to_hypercore(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
            ),
            check_mode=False,
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.do_shutdown_steps"
        ).return_value = None
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        nic_to_delete = Nic.from_hypercore(self._get_nic_1_dict())
        rest_client.delete_record.return_value = {"taskTag": "1234"}
        rest_client.get_record.side_effect = [self._get_nic_1_dict(), {"state": "Done"}]
        results = ManageVMNics.send_delete_nic_request_to_hypercore(
            VM.from_hypercore(self._get_empty_test_vm(), rest_client),
            module,
            rest_client=rest_client,
            nic_to_delete=nic_to_delete,
            before=[],
            after=[],
        )
        print(results)
        assert results == (True, [nic_to_delete.to_ansible()], [None], False)

    @classmethod
    def _get_empty_test_vm(cls):
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
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
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_uuid",
        }

    @classmethod
    def _get_test_vm(cls):
        nic_dict_1 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        nic_dict_2 = {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "RTL8139",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [nic_dict_1, nic_dict_2],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_uuid",
        }

    @classmethod
    def _get_test_vm_updated(cls):
        nic_dict_1 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 3,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        nic_dict_2 = {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 4,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [nic_dict_1, nic_dict_2],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_uuid",
        }

    @classmethod
    def _get_nic_2_updated(cls):
        return {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_2(cls):
        return {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "RTL8139",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_1_updated_vlan(cls):
        return {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 3,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_2_updated_vlan(cls):
        return {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 4,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_1_updated_mac(cls):
        return {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "INTEL_E1000",
            "macAddress": "12-34-56-78-AB",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }

    @classmethod
    def _get_nic_2_updated_mac(cls):
        return {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "INTEL_E1000",
            "macAddress": "AB-CD-EF-GH-12",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }

    def test_ensure_present_or_set_when_no_change_and_state_set(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
            )
        )
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )
        assert results == (False, [], {"before": [], "after": []}, False)

    def test_ensure_present_or_set_when_no_change_and_state_present(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
                state="present",
            )
        )
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (False, [], {"before": [], "after": []}, False)

    def test_ensure_present_or_set_when_changed_create_nics_and_state_set(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[{"vlan": 1, "type": "virtio"}, {"vlan": 2, "type": "RTL8139"}],
                state="set",
            )
        )
        rest_client.create_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1_dict(),
            {"state": ""},
            self._get_nic_2(),
            {"state": ""},
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "virtio",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "RTL8139",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [None, None],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
            False,
        )

    def test_ensure_present_or_set_when_changed_create_nics_and_state_present(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[{"vlan": 1, "type": "virtio"}, {"vlan": 2, "type": "RTL8139"}],
                state="present",
            )
        )
        rest_client.create_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1_dict(),
            {"state": ""},
            self._get_nic_2(),
            {"state": ""},
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "virtio",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "RTL8139",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [None, None],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
            False,
        )

    def test_ensure_present_or_set_when_changed_delete_all_and_state_set(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
            )
        )
        rest_client.delete_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
                "after": [],
            },
            True,
        )

    def test_ensure_present_or_set_when_changed_nic_type_and_state_present(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000"},
                    {"vlan": 2, "type": "INTEL_E1000"},
                ],
                state="present",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_dict(),
            {"state": ""},
            self._get_nic_2_updated(),
            {"state": ""},
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "INTEL_E1000",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "INTEL_E1000",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "INTEL_E1000",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "INTEL_E1000",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
            False,
        )

    def test_ensure_present_or_set_when_changed_nic_type_and_state_set(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000"},
                    {"vlan": 2, "type": "INTEL_E1000"},
                ],
                state="set",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_dict(),
            {"taskTag": "1234", "state": "COMPLETE"},
            self._get_nic_2_updated(),
            {"taskTag": "1234", "state": "COMPLETE"},
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "INTEL_E1000",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "INTEL_E1000",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "INTEL_E1000",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "INTEL_E1000",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
            False,
        )

    def test_ensure_present_or_set_when_changed_nic_vlan_and_state_present(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000", "vlan_new": 3},
                    {"vlan": 2, "type": "INTEL_E1000", "vlan_new": 4},
                ],
                state="present",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_vlan(),
            {"state": ""},
            self._get_nic_2_updated_vlan(),
            {"state": ""},
        ]
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 3,
                    "type": "INTEL_E1000",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    "mac": "00-00-00-00-00",
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 4,
                    "type": "INTEL_E1000",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    "mac": "00-00-00-00-00",
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 3,
                        "type": "INTEL_E1000",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 4,
                        "type": "INTEL_E1000",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
            },
            False,
        )

    def test_ensure_present_or_set_when_changed_nic_vlan_and_state_set(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000", "vlan_new": 3},
                    {"vlan": 2, "type": "INTEL_E1000", "vlan_new": 4},
                ],
                state="set",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.side_effect = [
            [self._get_test_vm()],
            [self._get_test_vm_updated()],
        ]
        rest_client.create_record.return_value = {
            "taskTag": "123",
            "state": "COMPLETED",
        }
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_vlan(),
            {"state": ""},
            self._get_nic_2_updated_vlan(),
            {"state": ""},
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 3,
                    "type": "INTEL_E1000",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    "mac": "00-00-00-00-00",
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 4,
                    "type": "INTEL_E1000",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    "mac": "00-00-00-00-00",
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 3,
                        "type": "INTEL_E1000",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 4,
                        "type": "INTEL_E1000",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
            },
            False,
        )

    def test_ensure_present_or_set_when_changed_nic_mac_and_state_present(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000", "mac_new": "12-34-56-78-AB"},
                    {"vlan": 2, "type": "INTEL_E1000", "mac_new": "AB-CD-EF-GH-12"},
                ],
                state="present",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_mac(),
            {"state": ""},
            self._get_nic_2_updated_mac(),
            {"state": ""},
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "INTEL_E1000",
                    "mac": "12-34-56-78-AB",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "INTEL_E1000",
                    "mac": "AB-CD-EF-GH-12",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "INTEL_E1000",
                        "mac": "12-34-56-78-AB",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "INTEL_E1000",
                        "mac": "AB-CD-EF-GH-12",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
            False,
        )

    def test_ensure_present_or_set_when_changed_nic_mac_and_state_set(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                unit_test=True,
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000", "mac_new": "12-34-56-78-AB"},
                    {"vlan": 2, "type": "INTEL_E1000", "mac_new": "AB-CD-EF-GH-12"},
                ],
                state="set",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "state": "COMPLETED",
        }
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_mac(),
            {"state": ""},
            self._get_nic_2_updated_mac(),
            {"state": ""},
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
        module_path = "scale_computing.hypercore.vm_nic"
        results = ManageVMNics.ensure_present_or_set(
            module=module, rest_client=rest_client, module_path=module_path
        )

        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "INTEL_E1000",
                    "mac": "12-34-56-78-AB",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "INTEL_E1000",
                    "mac": "AB-CD-EF-GH-12",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "INTEL_E1000",
                        "mac": "12-34-56-78-AB",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "INTEL_E1000",
                        "mac": "AB-CD-EF-GH-12",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
            False,
        )
