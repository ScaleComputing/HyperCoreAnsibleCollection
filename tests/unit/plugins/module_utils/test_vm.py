from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM
from ansible_collections.scale_computing.hypercore.plugins.module_utils.disk import Disk
from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors

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

        assert vm == VM.from_ansible(vm_dict)

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
            boot_devices=None,
            attach_guest_tools_iso=False,
            operating_system=None,
            node_affinity={
                "strict_affinity": False,
                "preferred_node": dict(
                    node_uuid=None,
                    backplane_ip=None,
                    lan_ip=None,
                    peer_id=None,
                ),
                "backup_node": dict(
                    node_uuid=None,
                    backplane_ip=None,
                    lan_ip=None,
                    peer_id=None,
                ),
            },
            snapshot_schedule_uuid="9238175f-2d6a-489f-9157-fa6345719b3b",
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
            bootDevices=None,
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
            power_state="started",
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
            state="RUNNING",
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
        )

    def test_find_disk(self):
        # TODO (domen): Write tests for find_disk, if necessary
        pass

    def test_create_payload_to_hc3(self):

        vm = VM(
            uuid=None,  # No uuid when creating object from ansible
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
        )

        assert vm.create_payload_to_hc3() == dict(
            options=dict(attachGuestToolsISO=False),
            dom=dict(
                name="VM-name",
                description="desc",
                mem=42,
                numVCPU=2,
                blockDevs=[],
                netDevs=[],
                bootDevices=[],
                tags="XLAB-test-tag1,XLAB-test-tag2",
                operatingSystem="os_windows_server_2012",
                state="RUNNING",
            ),
        )

    def test_update_payload_to_hc3(self):

        vm = VM(
            uuid=None,  # No uuid when creating object from ansible
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
        )

        assert vm.update_payload_to_hc3() == dict(
            dict(
                name="VM-name",
                description="desc",
                mem=42,
                numVCPU=2,
                blockDevs=[],
                netDevs=[],
                bootDevices=[],
                tags="XLAB-test-tag1,XLAB-test-tag2",
                uuid=None,
                operatingSystem="os_windows_server_2012",
                state="RUNNING",
            )
        )

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
            bootDevices=None,
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
                    node_uuid=None,
                    backplane_ip=None,
                    lan_ip=None,
                    peer_id=None,
                ),
                "backup_node": dict(
                    node_uuid=None,
                    backplane_ip=None,
                    lan_ip=None,
                    peer_id=None,
                ),
            },
            snapshot_schedule_uuid="snapshot_schedule_id",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
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
            name="jc1-disk-0",
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
        actual = VM.from_hypercore(
            vm_dict=rest_client.list_records.return_value[0], rest_client=rest_client
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
        rest_client.list_records.return_value = [vm_dict]
        virtual_machine = VM.get(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )[0]
        results = virtual_machine.delete_unused_nics_to_hypercore_vm(
            module.params, rest_client
        )
        assert results is False

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
        rest_client.list_records.return_value = [vm_dict]
        rest_client.delete_record.return_value = {"taskTag": "1234"}
        virtual_machine = VM.get(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )[0]
        results = virtual_machine.delete_unused_nics_to_hypercore_vm(
            module.params, rest_client
        )
        assert results is True

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
        rest_client.list_records.return_value = [vm_dict]
        rest_client.delete_record.side_effect = [
            {"taskTag": "1234"},
            {"taskTag": "5678"},
        ]
        virtual_machine = VM.get(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )[0]
        results = virtual_machine.delete_unused_nics_to_hypercore_vm(
            module.params, rest_client
        )
        assert results is True

    def test_find_nic_vlan(self, rest_client, mocker):
        virtual_machine = self._get_test_vm(rest_client, mocker)
        results = virtual_machine.find_nic(vlan=1)
        assert results[1] is (None)
        assert results[0].vlan == 1
        assert results[0].mac == "12-34-56-78-AB"
        assert results[0].uuid == "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"
        assert results[0].vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        assert results[0].connected is True

    def test_find_nic_vlan_and_vlan_new(self, rest_client, mocker):
        virtual_machine = self._get_test_vm(rest_client, mocker)
        results = virtual_machine.find_nic(vlan=2, vlan_new=1)
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

    def test_find_nic_mac(self, rest_client, mocker):
        virtual_machine = self._get_test_vm(rest_client, mocker)
        results = virtual_machine.find_nic(mac="12-34-56-78-CD")
        print(results)
        assert results[0].vlan == 2
        assert results[0].mac == "12-34-56-78-CD"
        assert results[0].uuid == "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"
        assert results[0].vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        assert results[0].connected is True

    def test_find_nic_mac_and_mac_new(self, rest_client, mocker):
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
        results = VM.create_export_or_import_vm_payload(
            "10.5.11.170", "/user", "username", "password", "this-vm-name", None, True
        )
        assert results == dict(
            target=dict(
                pathURI="smb://"
                + "username"
                + ":"
                + "password"
                + "@"
                + "10.5.11.170"
                + "/"
                + "/user"
            )
        )

    def test_export_vm(self, rest_client, mocker):
        ansible_dict = {
            "vm_name": "this-vm",
            "smb": {
                "server": "smb-server",
                "path": "/somewhere",
                "username": "user",
                "password": "pass",
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
        virtual_machine = VM.from_hypercore(smb_dict, rest_client)
        rest_client.list_records.return_value = [smb_dict]
        rest_client.create_record.return_value = {"taskTag": "12345"}
        results = virtual_machine.export_vm(rest_client, ansible_dict)
        assert results == {"taskTag": "12345"}


class TestVMImport:
    def test_create_export_or_import_vm_payload_when_import(self):
        results = VM.create_export_or_import_vm_payload(
            "10.5.11.170", "/user", "username", "password", "this-vm-name", None, False
        )
        print(results)
        assert results == dict(
            source=dict(
                pathURI="smb://"
                + "username"
                + ":"
                + "password"
                + "@"
                + "10.5.11.170"
                + "/"
                + "/user"
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
        virtual_machine = VM.from_hypercore(smb_dict, rest_client)
        rest_client.list_records.return_value = [smb_dict]
        rest_client.create_record.return_value = {"taskTag": "12345"}
        results = virtual_machine.import_vm(rest_client, ansible_dict)
        assert results == {"taskTag": "12345"}


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
        virtual_machine = VM.get_or_fail(
            query={"name": "XLAB-test-vm-clone"}, rest_client=rest_client
        )[0]
        results = virtual_machine.clone_vm(rest_client, ansible_dict)
        assert results == {"taskTag": "1234"}
