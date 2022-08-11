# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_nic
from ansible_collections.scale_computing.hypercore.plugins.module_utils.nic import Nic
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)

class TestNicCompare:
    def test_compare_same(self):
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        results = Nic.compare(existing_nic, new_nic)
        assert results == True


    def test_compare_different(self):
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2
        })
        results = Nic.compare(existing_nic, new_nic)
        assert results == False


    def test_compare_vlan_new(self):
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_ansible({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "vlan_new": 2
        })
        results = Nic.compare(existing_nic, new_nic)
        assert results == False    


    def test_compare_mac_new(self):
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_ansible({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "mac_new": "12:34:56:78:AB"
        })
        results = Nic.compare(existing_nic, new_nic)
        assert results == False


    def test_compare_mac_new_and_vlan_new(self):
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_ansible({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "vlan_new": 2,
            "mac_new": "12:34:56:78:AB"
        })
        results = Nic.compare(existing_nic, new_nic)
        assert results == False


    def test_compare_vlan_new_same(self):
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_ansible({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "vlan_new": 1,
        })
        results = Nic.compare(existing_nic, new_nic)
        print(results)
        assert results == True


    def test_compare_mac_new_same(self):
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "macAddress": "12:34:56:78:AB"
        })
        new_nic = Nic.create_from_ansible({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "mac_new": "12:34:56:78:AB"
        })
        results = Nic.compare(existing_nic, new_nic)
        print(results)
        assert results == True
        

    def test_compare_mac_new_and_vlan_new_same(self):
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "macAddress": "12:34:56:78:AB"
        })
        new_nic = Nic.create_from_ansible({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "vlan_new": 2,
            "mac_new": "12:34:56:78:AB"
        })
        results = Nic.compare(existing_nic, new_nic)
        print(results)
        assert results == True


class TestNicList:
    def test_create_nic_uuid_list_with_two_nics(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="unit_test_vm",
                state="present",
                items=[{
                    "vlan": 1
                },
                       {
                    "vlan": 2   
                }]
            )
        )
        
        results = vm_nic.create_nic_uuid_list(module)
        assert results == [1,2]


    def test_check_parameters_with_vm_uuid(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_uuid="9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece"
            )
        )
        results = vm_nic.check_parameters(module)
        assert results == None


    def test_delete_not_used_nics(self, client, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                items=[{
                    "vlan": 1
                },
                       {
                    "vlan": 2   
                }]
            )
        )
        end_point ="/rest/v1/VirDomain"
        virtual_machine = VM(from_hc3=False, vm_dict={})
        results = vm_nic.delete_not_used_nics(module, client, end_point, virtual_machine)
        assert results == None


class TestAbsent:
    def test_ensure_absent_nic_already_absent(self, client):
        end_point ="/rest/v1/VirDomainNetDevice"
        existing_nic = None

        results = vm_nic.ensure_absent(client, end_point, existing_nic)

        print(results)
        assert results == {"taskTag": "No task tag"}
    

    def test_ensure_absent_nic_is_present(self, client):
        end_point ="/rest/v1/VirDomainNetDevice"
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        client.request.return_value.json = {"taskTag": "1567"}

        results = vm_nic.ensure_absent(client, end_point, existing_nic)

        print(results)
        assert results == {"taskTag": "1567"}

class TestPresentAndSet:
    def test_ensure_present_or_set_when_nic_is_absent(self, client):
        end_point ="/rest/v1/VirDomainNetDevice"
        existing_nic = None
        new_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        
        client.request.return_value.json = {"taskTag": "1234"}
        results = vm_nic.ensure_present_or_set(client, end_point, existing_nic, new_nic)
        assert results == {"taskTag": "1234"}


    def test_ensure_present_or_set_when_nic_is_present_nics_are_the_same(self, client):
        end_point ="/rest/v1/VirDomainNetDevice"
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = existing_nic
        
        results = vm_nic.ensure_present_or_set(client, end_point, existing_nic, new_nic)
        assert results == {"taskTag": "No task tag"}
        
    def test_ensure_present_or_set_when_nic_is_present_nics_are_the_different(self, client):
        end_point ="/rest/v1/VirDomainNetDevice"
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2
        })
        
        client.request.return_value.json = {"taskTag": "1234"}
        results = vm_nic.ensure_present_or_set(client, end_point, existing_nic, new_nic)
        assert results == {"taskTag": "1234"}
        
    def test_ensure_present_or_set_when_nic_is_present_vlan_new(self, client):
        end_point ="/rest/v1/VirDomainNetDevice"
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_ansible({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "vlan_new": 3
        })
        
        client.request.return_value.json = {"taskTag": "1234"}
        results = vm_nic.ensure_present_or_set(client, end_point, existing_nic, new_nic)
        assert results == {"taskTag": "1234"}
        
    def test_ensure_present_or_set_when_nic_is_present_mac_new(self, client):
        end_point ="/rest/v1/VirDomainNetDevice"
        existing_nic = Nic.create_from_hc3({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1
        })
        new_nic = Nic.create_from_ansible({
            "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
            "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "mac_new": "12:34:56:78:AB"
        })
        
        client.request.return_value.json = {"taskTag": "1234"}
        results = vm_nic.ensure_present_or_set(client, end_point, existing_nic, new_nic)
        print(Nic.compare(existing_nic, new_nic))
        print(results)
        assert results == {"taskTag": "1234"}
