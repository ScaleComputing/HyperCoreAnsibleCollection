# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.nic import Nic
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import (
    ManageVMNics,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestNic:
    def test_init_from_ansible_data(self):
        ansible_data = dict(
            # uuid="my-uuid",  # always missing in ansible data?
            # many other fields can be missing too - more tests
            vlan=10,
            type="virtio",
            mac="12:00:00:00:00:00",
            connected=True,  # ATM ansible module does not allow setting connected flag
            # ipv4Addresses=['10.0.0.10', '10.0.1.10'],
        )
        nic = Nic.from_ansible(ansible_data)
        assert 10 == nic.vlan
        assert "virtio" == nic.type  # TODO fix, use enum
        assert "12:00:00:00:00:00" == nic.mac
        # ATM ansible module does not allow setting connected flag
        assert nic.connected is None
        assert [] == nic.ipv4Addresses

    @classmethod
    def _get_nic_from_hypercore(cls):
        hc3_data = dict(
            uuid="my-nic-uuid",
            virDomainUUID="my-vm-uuid",
            vlan=10,
            type="VIRTIO",
            macAddress="12:00:00:00:00:00",
            connected=True,
            ipv4Addresses=["10.0.0.10", "10.0.1.10"],
            # more fields?
        )
        return Nic.from_hypercore(hc3_data)

    @classmethod
    def _get_nic_1(cls):
        return Nic.from_hypercore(
            {
                "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "type": "virtio",
                "macAddress": "00-00-00-00-00",
                "connected": True,
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )

    @classmethod
    def _get_nic_1_updated(cls):
        return Nic.from_hypercore(
            {
                "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "type": "INTEL_E1000",
                "macAddress": "00-00-00-00-00",
                "connected": True,
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )

    def test_init_from_hypercore_data(self):
        nic = self._get_nic_from_hypercore()
        assert "my-nic-uuid" == nic.uuid
        assert 10 == nic.vlan
        assert "virtio" == nic.type
        assert "12:00:00:00:00:00" == nic.mac
        assert nic.connected is True
        assert ["10.0.0.10", "10.0.1.10"] == nic.ipv4Addresses

    def test_to_ansible(self):
        nic = self._get_nic_from_hypercore()
        ansible_data = nic.to_ansible()
        expected_data = dict(
            uuid="my-nic-uuid",
            vlan=10,
            type="virtio",
            mac="12:00:00:00:00:00",
            connected=True,
            ipv4_addresses=["10.0.0.10", "10.0.1.10"],
        )

        for kk in expected_data.keys():
            assert kk in ansible_data.keys()
            assert expected_data[kk] == ansible_data[kk]
        assert expected_data.keys() == ansible_data.keys()
        # assert below detects a difference, but does not tell back which key/value is problem.
        assert expected_data == ansible_data


class TestNicCompare:
    def test_compare_same(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "connected": True,
                "type": "virtio",
                "macAddress": "00-00-00-00-00",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "type": "virtio",
                "mac": "00-00-00-00-00",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is False

    def test_compare_different(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "connected": True,
                "type": "virtio",
                "macAddress": "00-00-00-00-00",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 2,
                "type": "virtio",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is True

    def test_compare_vlan_new_other(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "connected": True,
                "type": "virtio",
                "macAddress": "00-00-00-00-00",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "vlan_new": 2,
                "type": "virtio",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is True
        results = ManageVMNics.is_update_needed(new_nic, existing_nic)
        assert results is True

    def test_compare_vlan_new_self(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "connected": True,
                "type": "virtio",
                "macAddress": "00-00-00-00-00",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "vlan_new": 2,
                "type": "virtio",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is True

    def test_compare_mac_new(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "connected": True,
                "type": "virtio",
                "macAddress": "00-00-00-00-00",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "type": "virtio",
                "mac_new": "12:34:56:78:AB",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is True

    def test_compare_mac_new_and_vlan_new(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "connected": True,
                "type": "virtio",
                "macAddress": "00-00-00-00-00",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vlan": 1,
                "vlan_new": 2,
                "mac_new": "12:34:56:78:AB",
                "type": "virtio",
                "mac": "00-00-00-00-00",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is True

    def test_compare_vlan_new_same(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "macAddress": "12:34:56:78:AB",
                "connected": True,
                "type": "virtio",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "vlan_new": 1,
                "type": "virtio",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is False

    def test_compare_mac_new_same(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "macAddress": "12:34:56:78:AB",
                "connected": True,
                "type": "virtio",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "mac_new": "12:34:56:78:AB",
                "type": "virtio",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is False

    def test_compare_mac_new_and_vlan_new_same(self):
        existing_nic = Nic.from_hypercore(
            {
                "uuid": "9132f2ff-4f9b-43eb-8a91-6ce5bcf47ece",
                "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 2,
                "macAddress": "12:34:56:78:AB",
                "connected": True,
                "type": "virtio",
                "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            }
        )
        new_nic = Nic.from_ansible(
            {
                "vm_uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
                "vlan": 1,
                "vlan_new": 2,
                "mac_new": "12:34:56:78:AB",
                "type": "virtio",
            }
        )
        results = existing_nic.is_update_needed(new_nic)
        assert results is False
