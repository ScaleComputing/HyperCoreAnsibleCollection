# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    vm_replication_info,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRun:
    @classmethod
    def _get_empty_test_vm_1(cls):
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
            "machineType": "scale-7.2",
            "sourceVirDomainUUID": "",
        }

    @classmethod
    def _get_empty_test_vm_2(cls):
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ffs",
            "nodeUUID": "",
            "name": "XLAB_test_vm_2",
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
            "machineType": "scale-7.2",
            "sourceVirDomainUUID": "",
        }

    def test_run_with_vm_name(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
            )
        )
        vm_replication = {
            "uuid": "replication-uuid",
            "sourceDomainUUID": "vm-uuid",
            "enable": True,
            "connectionUUID": "remote-cluster-connection-uuid",
        }
        cluster_dict = {
            "remoteClusterInfo": {"clusterName": "remote-cluster-name"},
            "connectionStatus": "status",
            "replicationOK": "ok",
            "remoteNodeIPs": [],
            "remoteNodeUUIDs": [],
        }
        vm_dict = self._get_empty_test_vm_1()
        rest_client.get_record.return_value = cluster_dict
        rest_client.list_records.side_effect = [
            [vm_dict],
            [vm_replication],
            [vm_dict],
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        results = vm_replication_info.run(module, rest_client)

        assert results == (
            False,
            [
                {
                    "vm_name": "XLAB_test_vm",
                    "remote_cluster": "remote-cluster-name",
                    "state": "enabled",
                }
            ],
        )

    def test_run_without_vm_name(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
            )
        )
        module.params["vm_name"] = None
        vm_replication_1 = {
            "uuid": "replication-uuid",
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "enable": True,
            "connectionUUID": "remote-cluster-name",
        }
        vm_replication_2 = {
            "uuid": "replication-uuid-2",
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ffs",
            "enable": False,
            "connectionUUID": "remote-cluster-name",
        }
        cluster_dict = {
            "remoteClusterInfo": {"clusterName": "remote-cluster-name"},
            "connectionStatus": "status",
            "replicationOK": "ok",
            "remoteNodeIPs": [],
            "remoteNodeUUIDs": [],
        }
        vm_dict_1 = self._get_empty_test_vm_1()
        vm_dict_2 = self._get_empty_test_vm_2()
        rest_client.get_record.return_value = cluster_dict
        rest_client.list_records.side_effect = [
            [vm_replication_1, vm_replication_2],
            [vm_dict_1],
            [vm_dict_2],
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        results = vm_replication_info.run(module, rest_client)

        assert results == (
            False,
            [
                {
                    "vm_name": "XLAB_test_vm",
                    "remote_cluster": "remote-cluster-name",
                    "state": "enabled",
                },
                {
                    "vm_name": "XLAB_test_vm_2",
                    "remote_cluster": "remote-cluster-name",
                    "state": "disabled",
                },
            ],
        )


class TestMain:
    def test_minimal_set_of_params(self, run_main_info):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            vm_name=dict(
                type="str",
                required=False,
            ),
        )
        success, results = run_main_info(vm_replication_info, params)
        assert success is True
        assert results == {"changed": False, "records": []}
