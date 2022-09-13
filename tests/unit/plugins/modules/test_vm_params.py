from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_params
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


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
