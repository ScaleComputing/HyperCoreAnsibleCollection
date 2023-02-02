from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_clone
from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_minimal_set_of_params(self, run_main_info):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            vm_name=dict(
                type="str",
                required=True,
            ),
            source_vm_name=dict(
                type="str",
                required=True,
            ),
        )
        success, results = run_main_info(vm_clone, params)
        assert success is True
        assert results == {"changed": False, "msg": []}


class TestRun:
    @classmethod
    def _get_empty_vm_running(cls):
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
            "machineType": "scale-7.2",
        }
        return vm_dict

    @classmethod
    def _get_empty_vm(cls):
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
            "state": "SHUTOFF",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_id",
            "machineType": "scale-7.2",
        }
        return vm_dict

    def test_run_when_clone_already_exists(self, rest_client, create_module, mocker):
        module = module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB-test-vm-clone",
                source_vm_name="XLAB-test-vm",
            )
        )
        rest_client.list_records.side_effect = [[self._get_empty_vm()]]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = vm_clone.run(module, rest_client)
        assert result == (False, "Virtual machine XLAB-test-vm-clone already exists.")

    def test_run_when_VM_not_found(self, rest_client, create_module):
        module = module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB-test-vm-clone",
                source_vm_name="XLAB-test-vm",
            )
        )
        rest_client.list_records.side_effect = [[], []]
        with pytest.raises(
            errors.VMNotFound,
            match="Virtual machine - {'name': 'XLAB-test-vm'} - not found",
        ):
            vm_clone.run(module, rest_client)

    def test_run_when_VM_cloned(self, rest_client, create_module, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB-test-vm-clone",
                source_vm_name="XLAB-test-vm",
                tags=None,
            )
        )
        rest_client.get_record.side_effect = [None, None, {}, {"state": "COMPLETE"}]
        rest_client.create_record.return_value = {"taskTag": "1234"}
        rest_client.list_records.side_effect = [[], [self._get_empty_vm()]]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        results = vm_clone.run(module, rest_client)
        assert results == (
            True,
            "Virtual machine - XLAB-test-vm - cloning complete to - XLAB-test-vm-clone.",
        )

    def test_run_when_VM_cloned_with_tag_and_cloud_init(
        self, rest_client, create_module, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB-test-vm-clone",
                source_vm_name="XLAB-test-vm",
                tags="bla,bla1",
                cloud_init={
                    "user_data": "valid yaml",
                    "meta_data": "valid yaml aswell",
                },
            )
        )
        rest_client.get_record.side_effect = [None, None, {}, {"state": "COMPLETE"}]
        rest_client.create_record.return_value = {"taskTag": "1234"}
        rest_client.list_records.side_effect = [[], [self._get_empty_vm()]]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        results = vm_clone.run(module, rest_client)
        assert results == (
            True,
            "Virtual machine - XLAB-test-vm - cloning complete to - XLAB-test-vm-clone.",
        )
