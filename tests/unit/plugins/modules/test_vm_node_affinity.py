from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    vm_node_affinity,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM
from ansible_collections.scale_computing.hypercore.plugins.module_utils.node import Node
from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestGetNodeUuid:
    def test_get_node_uuid(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                strict_affinity=True,
                preferred_node={
                    "node_uuid": "preferred_node_uuid",
                    "backplane_ip": "preferred_node_backplane_ip",
                    "lan_ip": "preferred_node_lab_ip",
                    "peer_id": 1,
                },
                backup_node={
                    "node_uuid": "backup_node_uuid",
                    "backplane_ip": "backup_node_backplane_ip",
                    "lan_ip": "backup_node_lab_ip",
                    "peer_id": 2,
                },
            ),
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.Node.get_node"
        ).side_effect = [
            Node(
                node_uuid="preferred_node_uuid",
                backplane_ip="preferred_node_backplane_ip",
                lan_ip="preferred_node_lab_ip",
                peer_id=1,
            ),
            Node(
                node_uuid="backup_node_uuid",
                backplane_ip="backup_node_backplane_ip",
                lan_ip="backup_node_lab_ip",
                peer_id=2,
            ),
        ]

        preferred_node_uuid = vm_node_affinity.get_node_uuid(
            module, "preferred_node", rest_client
        )

        assert preferred_node_uuid == "preferred_node_uuid"

    def test_get_node_uuid_empty_string(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                strict_affinity=True,
                preferred_node={
                    "node_uuid": "",
                    "backplane_ip": "",
                    "lan_ip": "",
                    "peer_id": None,
                },
                backup_node={
                    "node_uuid": "",
                    "backplane_ip": "",
                    "lan_ip": "",
                    "peer_id": None,
                },
            ),
        )

        preferred_node_uuid = vm_node_affinity.get_node_uuid(
            module, "preferred_node", rest_client
        )

        assert preferred_node_uuid == ""

    def test_get_node_uuid_none(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                strict_affinity=True,
                preferred_node={
                    "node_uuid": None,
                    "backplane_ip": None,
                    "lan_ip": None,
                    "peer_id": None,
                },
                backup_node=None,
            ),
        )

        preferred_node_uuid = vm_node_affinity.get_node_uuid(
            module, "preferred_node", rest_client
        )
        backup_node_uuid = vm_node_affinity.get_node_uuid(
            module, "backup_node", rest_client
        )

        assert preferred_node_uuid is None
        assert backup_node_uuid is None

    def test_set_parameters_for_payload(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                strict_affinity=True,
                preferred_node={
                    "node_uuid": "preferred_node_uuid",
                    "backplane_ip": "preferred_node_backplane_ip",
                    "lan_ip": "preferred_node_lab_ip",
                    "peer_id": 1,
                },
                backup_node={
                    "node_uuid": "backup_node_uuid",
                    "backplane_ip": "backup_node_backplane_ip",
                    "lan_ip": "backup_node_lab_ip",
                    "peer_id": 2,
                },
            ),
        )

        vm = VM(
            uuid="vm_uuid",
            node_uuid="vm_node_uuid",
            name=None,
            tags=None,
            description=None,
            memory=None,
            power_state="stopped",
            vcpu=None,
            nics=None,
            disks=None,
            boot_devices=None,
            attach_guest_tools_iso=None,
            operating_system=None,
            node_affinity=dict(
                strict_affinity=False,
                preferred_node=dict(
                    node_uuid=None,
                    backplane_ip=None,
                    lan_ip=None,
                    peer_id=None,
                ),
                backup_node=dict(
                    node_uuid=None,
                    backplane_ip=None,
                    lan_ip=None,
                    peer_id=None,
                ),
            ),
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.get_node_uuid"
        ).side_effect = ["preferred_node_uuid", "backup_node_uuid"]

        (
            strict_affinity,
            preferred_node_uuid,
            backup_node_uuid,
        ) = vm_node_affinity.set_parameters_for_payload(module, vm, rest_client)

        assert strict_affinity is True
        assert preferred_node_uuid == "preferred_node_uuid"
        assert backup_node_uuid == "backup_node_uuid"

    def test_set_parameters_for_payload_nodes_not_provided(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                strict_affinity=True,
                preferred_node={
                    "node_uuid": None,
                },
                backup_node={
                    "node_uuid": None,
                },
            ),
        )

        vm = VM(
            uuid="vm_uuid",
            node_uuid="vm_node_uuid",
            name=None,
            tags=None,
            description=None,
            memory=None,
            power_state="stopped",
            vcpu=None,
            nics=None,
            disks=None,
            boot_devices=None,
            attach_guest_tools_iso=None,
            operating_system=None,
            node_affinity=dict(
                strict_affinity=False,
                preferred_node=dict(
                    node_uuid="preferred_node_uuid",
                    backplane_ip="preferred_backplane_ip",
                    lan_ip="preffered_lan_ip",
                    peer_id=1,
                ),
                backup_node=dict(
                    node_uuid="backup_node_uuid",
                    backplane_ip="backup_backplane_ip",
                    lan_ip="backup_lan_ip",
                    peer_id=2,
                ),
            ),
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.get_node_uuid"
        ).side_effect = [None, None]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.Node.get_node"
        )

        (
            strict_affinity,
            preferred_node_uuid,
            backup_node_uuid,
        ) = vm_node_affinity.set_parameters_for_payload(module, vm, rest_client)

        assert strict_affinity is True
        assert preferred_node_uuid == "preferred_node_uuid"
        assert backup_node_uuid == "backup_node_uuid"


class TestRun:
    def test_run(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                strict_affinity=True,
                preferred_node={
                    "node_uuid": "preferred_node_uuid",
                    "backplane_ip": "preferred_node_backplane_ip",
                    "lan_ip": "preferred_node_lab_ip",
                    "peer_id": 1,
                },
                backup_node={
                    "node_uuid": "backup_node_uuid",
                    "backplane_ip": "backup_node_backplane_ip",
                    "lan_ip": "backup_node_lab_ip",
                    "peer_id": 2,
                },
            ),
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.set_parameters_for_payload"
        ).return_value = (True, "preferred_node_uuid", "backup_node_uuid")
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.TaskTag.wait_task"
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.VM.get_by_name"
        ).return_value = VM(
            uuid="vm_uuid",
            node_uuid="vm_node_uuid",
            name=None,
            tags=None,
            description=None,
            memory=None,
            power_state="stopped",
            vcpu=None,
            nics=None,
            disks=None,
            boot_devices=None,
            attach_guest_tools_iso=None,
            operating_system=None,
            node_affinity=dict(
                strict_affinity=False,
                preferred_node=dict(
                    node_uuid=None,
                    backplane_ip=None,
                    lan_ip=None,
                    peer_id=None,
                ),
                backup_node=dict(
                    node_uuid=None,
                    backplane_ip=None,
                    lan_ip=None,
                    peer_id=None,
                ),
            ),
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.RestClient.update_record"
        )

        changed, msg, diff = vm_node_affinity.run(module, rest_client)

        assert changed is True
        assert msg == "Node affinity successfully updated."

    def test_run_invalid_parameters(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                strict_affinity=True,
                preferred_node={
                    "node_uuid": None,
                },
                backup_node={
                    "node_uuid": None,
                },
            ),
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.VM.get_by_name"
        ).return_value = VM(
            uuid="vm_uuid",
            node_uuid="vm_node_uuid",
            name=None,
            tags=None,
            description=None,
            memory=None,
            power_state="stopped",
            vcpu=None,
            nics=None,
            disks=None,
            boot_devices=None,
            attach_guest_tools_iso=None,
            operating_system=None,
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
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.set_parameters_for_payload"
        ).return_value = (True, "", "")
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.RestClient.update_record"
        )

        with pytest.raises(errors.VMInvalidParams) as exc:
            vm_node_affinity.run(module, rest_client)

        assert (
            "Invalid set of parameters - strict affinity set to true and nodes not provided."
            in str(exc.value)
        )

    def test_run_no_change(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-name-unique",
                strict_affinity=True,
                preferred_node={
                    "node_uuid": "preferred_node_uuid",
                    "backplane_ip": "preferred_node_backplane_ip",
                    "lan_ip": "preferred_node_lab_ip",
                    "peer_id": 1,
                },
                backup_node={
                    "node_uuid": "backup_node_uuid",
                    "backplane_ip": "backup_node_backplane_ip",
                    "lan_ip": "backup_node_lab_ip",
                    "peer_id": 2,
                },
            ),
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.VM.get_by_name"
        ).return_value = VM(
            uuid="vm_uuid",
            node_uuid="",
            name=None,
            tags=None,
            description=None,
            memory=None,
            power_state="stopped",
            vcpu=None,
            nics=None,
            disks=None,
            boot_devices=None,
            attach_guest_tools_iso=None,
            operating_system=None,
            node_affinity=dict(
                strict_affinity=True,
                preferred_node=dict(
                    node_uuid="preferred_node_uuid",
                    backplane_ip="preferred_node_backplane_ip",
                    lan_ip="preferred_node_lab_ip",
                    peer_id=1,
                ),
                backup_node=dict(
                    node_uuid="backup_node_uuid",
                    backplane_ip="backup_node_backplane_ip",
                    lan_ip="backup_node_lab_ip",
                    peer_id=2,
                ),
            ),
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.set_parameters_for_payload"
        ).return_value = (True, "preferred_node_uuid", "backup_node_uuid")
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.vm_node_affinity.RestClient.update_record"
        )

        changed, msg, diff = vm_node_affinity.run(module, rest_client)

        assert changed is False
        assert msg == "Node affinity already set to desired values."


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-name-unique",
            strict_affinity=False,
            preferred_node={
                "node_uuid": "preferred_node_uuid",
                "backplane_ip": "preferred_node_backplane_ip",
                "lan_ip": "preferred_node_lab_ip",
                "peer_id": 1,
            },
            backup_node={
                "node_uuid": "backup_node_uuid",
                "backplane_ip": "backup_node_backplane_ip",
                "lan_ip": "backup_node_lab_ip",
                "peer_id": 2,
            },
        )
        success, result = run_main(vm_node_affinity, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-name-unique",
            strict_affinity=False,
        )
        success, result = run_main(vm_node_affinity, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(vm_node_affinity)

        assert success is False
        # ansible2.9+py3.8 has order "vm_name, strict_affinity"
        # print("result.msg={}".format(result["msg"]))
        assert (
            "missing required arguments: strict_affinity, vm_name" in result["msg"]
            or "missing required arguments: vm_name, strict_affinity" in result["msg"]
        )
