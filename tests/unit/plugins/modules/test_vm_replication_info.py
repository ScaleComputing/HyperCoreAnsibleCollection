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
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestCreateOutput:
    def test_create_output_empty(self):
        records = {}
        results = vm_replication_info.create_output(records)
        assert results == (False, {})

    def test_create_output_not_empty(self):
        records = {
            "vm_name": "XLAB_test_vm",
            "remote_cluster": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
            "state": "disabled",
        }
        results = vm_replication_info.create_output(records)
        assert results == (
            False,
            {
                "vm_name": "XLAB_test_vm",
                "remote_cluster": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
                "state": "disabled",
            },
        )


class TestFindReplication:
    def test_find_replication_while_replication_not_exists(self, rest_client, client):
        vm_dict = {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [],
            "stats": "bla",
            "tags": "XLAB,test",
        }
        client.get.return_value.json = [vm_dict]
        rest_client.list_records.return_value = []
        virtual_machine_obj = VM.from_hypercore(vm_dict=vm_dict)
        results = vm_replication_info.find_replication(rest_client, virtual_machine_obj)
        assert results == []

    def test_find_replication_while_replication_exists(self, rest_client, client):
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
        client.get.return_value.json = [vm_dict]
        rest_client.list_records.return_value = [hypercore_data]
        virtual_machine_obj = VM.from_hypercore(vm_dict=vm_dict)
        results = vm_replication_info.find_replication(rest_client, virtual_machine_obj)
        print(results)
        assert results == [
            {
                "vm_name": "XLAB_test_vm",
                "remote_cluster": "7890f2ab-3r9a-89ff-5k91-3gdahgh47ghg",
                "state": "disabled",
            }
        ]
