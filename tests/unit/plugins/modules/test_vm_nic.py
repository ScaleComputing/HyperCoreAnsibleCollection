# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_nic

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestEnsurePresentOrSet:
    @classmethod
    def _get_empty_test_vm(cls):
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
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
        }

    @classmethod
    def _get_test_vm(cls):
        nic_dict_1 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        nic_dict_2 = {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "RTL8139",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [nic_dict_1, nic_dict_2],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
        }

    @classmethod
    def _get_test_vm_updated(cls):
        nic_dict_1 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 3,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        nic_dict_2 = {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 4,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [nic_dict_1, nic_dict_2],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
        }

    @classmethod
    def _get_nic_1(cls):
        return {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_1_updated(cls):
        return {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_2_updated(cls):
        return {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_2(cls):
        return {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "RTL8139",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_1_updated_vlan(cls):
        return {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 3,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_2_updated_vlan(cls):
        return {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 4,
            "type": "INTEL_E1000",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }

    @classmethod
    def _get_nic_1_updated_mac(cls):
        return {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "INTEL_E1000",
            "macAddress": "12-34-56-78-AB",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }

    @classmethod
    def _get_nic_2_updated_mac(cls):
        return {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "INTEL_E1000",
            "macAddress": "AB-CD-EF-GH-12",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }

    def test_ensure_present_or_set_when_no_change_and_state_set(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
            )
        )
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (False, [], {"before": [], "after": []})

    def test_ensure_present_or_set_when_no_change_and_state_present(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[],
                state="present",
            )
        )
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (False, [], {"before": [], "after": []})

    def test_ensure_present_or_set_when_changed_create_nics_and_state_set(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[{"vlan": 1, "type": "virtio"}, {"vlan": 2, "type": "RTL8139"}],
                state="set",
            )
        )
        rest_client.create_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1(),
            {"state": ""},
            self._get_nic_2(),
            {"state": ""},
        ]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "virtio",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "RTL8139",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [None, None],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
        )

    def test_ensure_present_or_set_when_changed_create_nics_and_state_present(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[{"vlan": 1, "type": "virtio"}, {"vlan": 2, "type": "RTL8139"}],
                state="present",
            )
        )
        rest_client.create_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1(),
            {"state": ""},
            self._get_nic_2(),
            {"state": ""},
        ]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "virtio",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "RTL8139",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [None, None],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
        )

    def test_ensure_present_or_set_when_changed_delete_all_and_state_set(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[],
                state="set",
            )
        )
        rest_client.delete_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
                "after": [],
            },
        )

    def test_ensure_present_or_set_when_changed_nic_type_and_state_present(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000"},
                    {"vlan": 2, "type": "INTEL_E1000"},
                ],
                state="present",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated(),
            {"state": ""},
            self._get_nic_2_updated(),
            {"state": ""},
        ]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "INTEL_E1000",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "INTEL_E1000",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "INTEL_E1000",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "INTEL_E1000",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
        )

    def test_ensure_present_or_set_when_changed_nic_type_and_state_set(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000"},
                    {"vlan": 2, "type": "INTEL_E1000"},
                ],
                state="set",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated(),
            {"state": ""},
            self._get_nic_2_updated(),
            {"state": ""},
        ]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "INTEL_E1000",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "INTEL_E1000",
                    "mac": "00-00-00-00-00",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "INTEL_E1000",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "INTEL_E1000",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
        )

    def test_ensure_present_or_set_when_changed_nic_vlan_and_state_present(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000", "vlan_new": 3},
                    {"vlan": 2, "type": "INTEL_E1000", "vlan_new": 4},
                ],
                state="present",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_vlan(),
            {"state": ""},
            self._get_nic_2_updated_vlan(),
            {"state": ""},
        ]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 3,
                    "type": "INTEL_E1000",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    "mac": "00-00-00-00-00",
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 4,
                    "type": "INTEL_E1000",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    "mac": "00-00-00-00-00",
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 3,
                        "type": "INTEL_E1000",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 4,
                        "type": "INTEL_E1000",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
            },
        )

    def test_ensure_present_or_set_when_changed_nic_vlan_and_state_set(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000", "vlan_new": 3},
                    {"vlan": 2, "type": "INTEL_E1000", "vlan_new": 4},
                ],
                state="set",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.side_effect = [
            [self._get_test_vm()],
            [self._get_test_vm_updated()],
        ]
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_vlan(),
            {"state": ""},
            self._get_nic_2_updated_vlan(),
            {"state": ""},
        ]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 3,
                    "type": "INTEL_E1000",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    "mac": "00-00-00-00-00",
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 4,
                    "type": "INTEL_E1000",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    "mac": "00-00-00-00-00",
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 3,
                        "type": "INTEL_E1000",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 4,
                        "type": "INTEL_E1000",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
            },
        )

    def test_ensure_present_or_set_when_changed_nic_mac_and_state_present(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000", "mac_new": "12-34-56-78-AB"},
                    {"vlan": 2, "type": "INTEL_E1000", "mac_new": "AB-CD-EF-GH-12"},
                ],
                state="present",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_mac(),
            {"state": ""},
            self._get_nic_2_updated_mac(),
            {"state": ""},
        ]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "INTEL_E1000",
                    "mac": "12-34-56-78-AB",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "INTEL_E1000",
                    "mac": "AB-CD-EF-GH-12",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "INTEL_E1000",
                        "mac": "12-34-56-78-AB",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "INTEL_E1000",
                        "mac": "AB-CD-EF-GH-12",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
        )

    def test_ensure_present_or_set_when_changed_nic_mac_and_state_set(
        self, rest_client, create_module
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[
                    {"vlan": 1, "type": "INTEL_E1000", "mac_new": "12-34-56-78-AB"},
                    {"vlan": 2, "type": "INTEL_E1000", "mac_new": "AB-CD-EF-GH-12"},
                ],
                state="set",
            )
        )
        rest_client.update_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.get_record.side_effect = [
            self._get_nic_1_updated_mac(),
            {"state": ""},
            self._get_nic_2_updated_mac(),
            {"state": ""},
        ]
        results = vm_nic.ensure_present_or_set(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [
                {
                    "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 1,
                    "type": "INTEL_E1000",
                    "mac": "12-34-56-78-AB",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
                {
                    "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                    "vlan": 2,
                    "type": "INTEL_E1000",
                    "mac": "AB-CD-EF-GH-12",
                    "connected": True,
                    "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                },
            ],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "mac": "00-00-00-00-00",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
                "after": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "INTEL_E1000",
                        "mac": "12-34-56-78-AB",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "INTEL_E1000",
                        "mac": "AB-CD-EF-GH-12",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                    },
                ],
            },
        )


class TestEnsureAbsent:
    @classmethod
    def _get_empty_test_vm(cls):
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
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
        }

    @classmethod
    def _get_test_vm(cls):
        nic_dict_1 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        nic_dict_2 = {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "RTL8139",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [nic_dict_1, nic_dict_2],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
        }

    def test_ensure_absent_when_no_change(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[],
                state="absent",
            )
        )
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        results = vm_nic.ensure_absent(module=module, rest_client=rest_client)
        print(results)
        assert results == (False, [], {"before": [], "after": []})

    def test_ensure_absent_when_change(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[{"vlan": 1}, {"vlan": 2}],
                state="absent",
            )
        )
        rest_client.delete_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        rest_client.list_records.return_value = [self._get_test_vm()]
        results = vm_nic.ensure_absent(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [None, None],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
                "after": [None, None],
            },
        )


class TestMain:
    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            state="present",
            vm_name=dict(
                type="str",
                required=True,
            ),
            items=[],
        )
        success, results = run_main(vm_nic, params)
        print(success)
        print(results)
        assert success is True
        assert results == {
            "changed": False,
            "records": {},
            "diff": {"before": {}, "after": {}},
        }
