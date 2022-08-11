# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_nic
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM

import json
import uuid

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)

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

