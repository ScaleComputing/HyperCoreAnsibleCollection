# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM
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
        rest_client.get_record.return_value = None
        results = Replication.get(
            rest_client=rest_client, vm_uuid="7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        )
        assert results is None

    def test_get_vm_exist(self, rest_client):
        hypercore_data = {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": False,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
        }
        rest_client.get_record.return_value = hypercore_data
        results = Replication.get(
            rest_client=rest_client, vm_uuid="7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg"
        )
        assert results == [{
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": False,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
        }]


class TestCreateFromHypercore:
    def test_create_from_hypercore(self):
        hypercore_data = {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": False,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
        }
        vm_dict = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [],
            "stats": "bla",
            "tags": "XLAB,test",
        }
        virtual_machine_obj = VM(from_hc3=True, vm_dict=vm_dict)
        replication_obj = Replication.create_from_hypercore(
            hypercore_data, virtual_machine_obj
        )
        assert replication_obj.vm_uuid == hypercore_data["sourceDomainUUID"]
        assert replication_obj.vm_name == vm_dict["name"]
        assert replication_obj.replication_uuid == hypercore_data["uuid"]
        assert replication_obj.state == Replication.handle_state(
            hypercore_data["enable"]
        )
        assert (
            replication_obj.remote_cluster_connection_uuid
            == hypercore_data["connectionUUID"]
        )


class TestDataToAnsible:
    def test_data_to_ansible(self):
        hypercore_data = {
            "sourceDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "uuid": "8972f2as-179a-67af-66a1-6uiahgf47ffs",
            "enable": False,
            "connectionUUID": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
        }
        vm_dict = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [],
            "stats": "bla",
            "tags": "XLAB,test",
        }
        virtual_machine_obj = VM(from_hc3=True, vm_dict=vm_dict)
        replication_obj = Replication.create_from_hypercore(
            hypercore_data, virtual_machine_obj
        )
        replication_dict = replication_obj.data_to_ansible()

        assert replication_dict == {
            "vm_name": "XLAB_test_vm",
            "remote_cluster": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "state": "disabled",
        }
