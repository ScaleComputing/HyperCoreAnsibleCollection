from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_export
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
            smb=dict(
                server=dict(
                    type="str",
                    required=True,
                ),
                path=dict(
                    type="str",
                    required=True,
                ),
                username=dict(
                    type="str",
                    required=True,
                ),
                password=dict(
                    type="str",
                    no_log=True,
                    required=True,
                ),
            ),
        )

        success, results = run_main_info(vm_export, params)

        assert success is True
        assert results == {"changed": False, "msg": []}


class TestRun:
    def test_run_when_VM_found(self, create_module, rest_client, mocker):
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
        }
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB-test-vm",
                smb={
                    "server": "test-server",
                    "path": "/somewhere/else",
                    "username": "user",
                    "password": "pass",
                    "file_name": None,
                },
                http_uri=None,
            )
        )
        rest_client.list_records.side_effect = [[vm_dict], [smb_dict]]
        rest_client.get_record.return_value = {"state": "COMPLETE"}
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "createdUUID": "uuid",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None

        results = vm_export.run(module, rest_client)

        assert results == (
            True,
            "Virtual machine - XLAB-test-vm - export complete to - test-server",
        )

    def test_run_when_VM_not_found(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB-test-vm",
                smb={
                    "server": "test-server",
                    "path": "/somewhere/else",
                    "username": "user",
                    "password": "pass",
                },
                http_uri=None,
            )
        )
        rest_client.list_records.return_value = []

        with pytest.raises(
            errors.VMNotFound,
            match="Virtual machine - {'name': 'XLAB-test-vm'} - not found",
        ):
            vm_export.run(module, rest_client)
