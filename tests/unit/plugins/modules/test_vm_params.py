from __future__ import absolute_import, division, print_function

from ansible_collections.scale_computing.hypercore.plugins.module_utils.snapshot_schedule import (
    SnapshotSchedule,
)

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_params
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestBuildPayload:
    def test_build_payload(self, rest_client, create_module, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_params.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = SnapshotSchedule(
            name="snapshot_schedule",
            uuid="snapshot_schedule_uuid",
            recurrences=None,
        )

        payload = vm_params.build_payload(module, rest_client)

        assert payload == {
            "name": "VM-unique-name-updated",
            "description": "Updated parameters",
            "tags": "Xlab",
            "mem": 512,
            "numVCPU": 2,
            "snapshotScheduleUUID": "snapshot_schedule_uuid",
        }

    def test_build_payload_empty_strings(self, rest_client, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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

        payload = vm_params.build_payload(module, rest_client)

        assert payload == {
            "name": "VM-unique-name-updated",
            "description": "",
            "tags": "",
            "mem": 512,
            "numVCPU": 2,
            "snapshotScheduleUUID": "",
        }

    def test_to_be_changed(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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

        changed, changed_parameters = vm_params.to_be_changed(vm, module)
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
                vm_name="old_name",
                vm_name_new="new_name",
                description="",
                tags="",
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

        changed, changed_parameters = vm_params.to_be_changed(vm, module)
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

    def test_needs_reboot(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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
        reboot_needed = vm_params.needs_reboot(module, changed)

        assert reboot_needed is True

    def test_doesnt_need_reboot(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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
        reboot_needed = vm_params.needs_reboot(module, changed)

        assert reboot_needed is False

    def test_build_before_diff(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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

        assert before == vm_params.build_before_diff(vm_before, module)

    def test_build_after_diff(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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

        assert after == vm_params.build_after_diff(module, rest_client)

    def test_build_after_diff_check_mode(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
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

        assert after == vm_params.build_after_diff(module, rest_client)


class TestRun:
    def test_run(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="old_name",
                vm_name_new="new_name",
                description="Updated description",
                tags=["Xlab"],
                memory=512,
                vcpu=4,
                power_state="started",
                snapshot_schedule="",
            ),
            check_mode=True,
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_params.VM.get_by_name"
        ).return_value = VM(
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
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_params.VM.update_vm_power_state"
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_params.RestClient.update_record"
        )

        changed, reboot_needed, diff = vm_params.run(module, rest_client)

        assert changed is True
        assert reboot_needed is True
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

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_params.VM.get_by_name"
        ).return_value = VM(
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
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_params.VM.update_vm_power_state"
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_params.RestClient.update_record"
        )

        changed, reboot_needed, diff = vm_params.run(module, rest_client)

        assert changed is False
        assert reboot_needed is False
        assert diff == {
            "before": None,
            "after": None,
        }


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-unique-name",
            vm_name_new="VM-unique-name-updated",
            description="Updated parameters",
            tags=["Xlab"],
            memory=512,
            vcpu=2,
            power_state="start",
            snapshot_schedule="snapshot_schedule",
        )
        success, result = run_main(vm_params, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-name-unique",
        )
        success, result = run_main(vm_params, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(vm_params)

        assert success is False
        assert "missing required arguments: vm_name" in result["msg"]
