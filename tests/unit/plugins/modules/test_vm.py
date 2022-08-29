from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestEnsureAbsent:
    def test_ensure_absent_record_present(self, create_module, rest_client, task_wait):
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
                cloud_init=None,
                attach_guest_tools_iso=None,
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
            bootDevices=None,
            attachGuestToolsISO=False,
            operatingSystem=None,
            affinityStrategy={
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
        )

        rest_client.delete_record.return_value = None
        result = vm.ensure_absent(module, rest_client)
        rest_client.delete_record.assert_called_once()
        assert result == (
            True,
            None,
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
                cloud_init=None,
                attach_guest_tools_iso=None,
            ),
        )

        rest_client.get_record.return_value = None

        result = vm.ensure_absent(module, rest_client)
        assert result == (False, dict())


class TestEnsurePresent:
    def test_ensure_present_record_present(self, create_module, rest_client, task_wait):
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
        )

        rest_client.update_record.return_value = dict(
            vm_name="VM-unique-name-updated",
            uuid="id",
        )

        vm.ensure_present(module, rest_client)
        rest_client.update_record.assert_called_once()
        rest_client.create_record.assert_not_called()

    def test_ensure_present_record_absent(self, create_module, rest_client, task_wait):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-unique-name",
                uuid="id",
                description=None,
                memory=42,
                vcpu=2,
                power_state="started",
                state="absent",
                tags="",
                disks=None,
                nics=None,
                boot_devices=None,
                attach_guest_tools_iso=None,
            ),
        )

        rest_client.get_record.return_value = None
        rest_client.create_record.return_value = None
        vm.ensure_present(module, rest_client)
        rest_client.create_record.assert_called_once()
        rest_client.update_record.assert_not_called()
