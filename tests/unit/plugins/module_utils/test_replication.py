# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.replication import (
    Replication,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestState:
    def test_handle_state_enabled(self):
        enabled = True
        results = Replication.handle_state(enable=enabled)
        assert results == "enabled"

    def test_handle_state_disabled(self):
        enabled = False
        results = Replication.handle_state(enable=enabled)
        assert results == "disabled"

    def test_handle_state_None(self):
        enabled = None
        results = Replication.handle_state(enable=enabled)
        assert results == "disabled"


class TestGet:
    def test_get_vm_not_exist(self, rest_client):
        rest_client.list_records.return_value = []
        results = Replication.get(
            rest_client=rest_client,
            query={"sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"},
        )
        assert results == []

    def test_get_vm_exist(self, rest_client, mocker):
        hypercore_data = {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": False,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "remote_cluster": "cluster-name",
            "vm_name": "test-vm",
        }
        remote_cluster_dict = {
            "remoteClusterInfo": {"clusterName": "remote-cluster-name"},
            "connectionStatus": "status",
            "replicationOK": "ok",
            "remoteNodeIPs": [],
            "remoteNodeUUIDs": [],
        }
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
        rest_client.get_record.return_value = remote_cluster_dict
        rest_client.list_records.side_effect = [
            [hypercore_data],
            [vm_dict],
        ]
        results = Replication.get(
            rest_client=rest_client,
            query={"sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"},
        )[0]
        assert results.replication_uuid == "8972f2as-179a-67af-66a1-6uiahgf47ffs"
        assert results.state == "disabled"
        assert results.connection_uuid == "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg"
        assert results.vm_uuid == "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"


class TestCreateFromHypercore:
    def test_create_from_hypercore(self):
        hypercore_data = {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": False,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "vm_name": "test-vm",
            "remote_cluster": "remote-cluster-name",
        }
        replication_obj = Replication.from_hypercore(hypercore_data)
        assert replication_obj.vm_uuid == hypercore_data["sourceDomainUUID"]
        assert replication_obj.replication_uuid == hypercore_data["uuid"]
        assert replication_obj.state == Replication.handle_state(
            hypercore_data["enable"]
        )
        assert replication_obj.connection_uuid == hypercore_data["connectionUUID"]
        assert replication_obj.vm_name == "test-vm"
        assert replication_obj.remote_cluster == "remote-cluster-name"


class TestDataToAnsible:
    def test_data_to_ansible(self):
        hypercore_data = {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": False,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "remote_cluster": "cluster-name",
            "vm_name": "XLAB_test_vm",
        }
        replication_obj = Replication.from_hypercore(hypercore_data)
        replication_dict = replication_obj.to_ansible()

        assert replication_dict == {
            "vm_name": "XLAB_test_vm",
            "remote_cluster": "cluster-name",
            "state": "disabled",
        }


class TestToHypercore:
    def test_to_hypercore_when_enable_false(self):
        hypercore_data = {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": False,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "remote_cluster": "remote-cluster-name",
            "vm_name": "test-vm",
        }
        replication_obj = Replication.from_hypercore(hypercore_data)
        results = replication_obj.to_hypercore()
        print(results)
        assert results == {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "enable": False,
        }

    def test_to_hypercore_when_enable_true(self):
        hypercore_data = {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": True,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "remote_cluster": "remote-cluster-name",
            "vm_name": "test-vm",
        }
        replication_obj = Replication.from_hypercore(hypercore_data)
        results = replication_obj.to_hypercore()
        print(results)
        assert results == {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "enable": True,
        }
