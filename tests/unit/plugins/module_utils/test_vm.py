from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM

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

    def test_vm_from_hypercore_dict_is_not_none(self):
        vm = VM(
            uuid="",  # No uuid when creating object from ansible
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
        )

        vm_dict = dict(
            uuid="",
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
        )

        vm_from_hypercore = VM.from_hypercore(vm_dict)
        assert vm == vm_from_hypercore

    def test_vm_from_hypercore_dict_is_none(self):
        vm = None
        vm_dict = None
        vm_from_hypercore = VM.from_hypercore(vm_dict)
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
        )

    def test_find_nic(self):
        # TODO (domen): Write tests for find_nic, if necessary
        pass

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
        ) == VM(
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

    def test_equal_false(self):
        assert VM(
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
        ) != VM(
            uuid=None,  # No uuid when creating object from ansible
            name="VM   NAME    CHANGED !!!!!!",
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

    def test_compare(self):
        hypercore_dict = dict(
            uuid=None,
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
        )

        ansible_dict = dict(
            uuid=None,  # No uuid when creating object from ansible
            vm_name="VM-name",
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
        )

        assert VM.compare(ansible_dict, hypercore_dict)

    def test_get_by_name(self, rest_client):
        ansible_dict = dict(
            vm_name="vm-name",
        )
        rest_client.get_record.return_value = dict(
            uuid="id",
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
        )

        vm_by_name = VM.get_by_name(ansible_dict, rest_client)
        assert vm == vm_by_name
