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

import json

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)

class TestAbsent:
    def test_ensure_absent(self, client, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="unit_test_vm",
                state="present",
            )
        )
        existing_nic = Nic.create_from_hc3(
            {
                "virDomainUUID": "1234-5678-9101",
                "uuid": "1234-5678-9101",
                "type": "virtio",
                "mac": None,
                "vlan": 1,
                "connected": True,
                "ipv4Addresses": []
            }
        )
        end_point="/rest/v1/VirDomain"
        client.request.return_value = json.dumps({"bla": 1})
        results = vm_nic.do_absent(client, end_point, existing_nic)
        print(results)
        assert results == {}
