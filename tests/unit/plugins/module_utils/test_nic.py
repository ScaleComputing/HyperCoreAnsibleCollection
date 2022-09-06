# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.nic import Nic

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
            print("kk=%s {%s} =?= {%s}" % (kk, expected_data[kk], ansible_data[kk]))
            assert kk in ansible_data.keys()
            assert expected_data[kk] == ansible_data[kk]
        assert expected_data.keys() == ansible_data.keys()
        # assert below detects a difference, but does not tell back which key/value is problem.
        assert expected_data == ansible_data

    def test_get_by_uuid(self, rest_client):
        nic = dict(
            uuid="my-nic-uuid",
            virDomainUUID="my-vm-uuid",
            vlan=10,
            type="VIRTIO",
            macAddress="12:00:00:00:00:00",
            connected=True,
            ipv4Addresses=["10.0.0.10", "10.0.1.10"],
            # more fields?
        )
        nic_dict = nic
        rest_client.get_record.return_value = nic_dict
        results = Nic.get_by_uuid(rest_client=rest_client, nic_uuid="my-nic-uuid")
        print(results)
        nic_dict = Nic.from_hypercore(nic_dict).to_hypercore()
        assert results.to_hypercore() == nic_dict

    def test_send_update_nic_to_hypercore(self, rest_client):
        existing_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        new_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "INTEL_E1000",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        rest_client.update_record.return_value = {"taskTag": "1234"}
        rest_client.get_record.side_effect = [new_nic, {"state": "Done"}]
        results = Nic.send_update_nic_request_to_hypercore(
            rest_client=rest_client,
            new_nic=Nic.from_hypercore(new_nic),
            existing_nic=Nic.from_hypercore(existing_nic),
            before=[],
            after=[],
        )
        existing_nic = Nic.from_hypercore(existing_nic)
        new_nic = Nic.from_hypercore(new_nic)
        assert results == (True, [existing_nic.to_ansible()], [new_nic.to_ansible()])

    def test_send_create_nic_to_hypercore(self, rest_client):
        new_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "macAddress": "00-00-00-00-00",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
        }
        rest_client.get_record.side_effect = [new_nic, {"state": "Done"}]
        results = Nic.send_create_nic_request_to_hypercore(
            rest_client=rest_client,
            new_nic=Nic.from_hypercore(new_nic),
            before=[],
            after=[],
        )
        print(results)
        print((True, [None], [Nic.from_hypercore(new_nic).to_ansible()]))
        assert results == (True, [None], [Nic.from_hypercore(new_nic).to_ansible()])

    def test_send_delete_nic_request_to_hypercore(self, rest_client):
        nic_to_delete = self._get_nic_1()
        rest_client.delete_record.return_value = {"taskTag": "1234"}
        rest_client.get_record.side_effect = [{"state": "Done"}]
        results = Nic.send_delete_nic_request_to_hypercore(
            rest_client=rest_client, nic_to_delete=nic_to_delete, before=[], after=[]
        )
        print(results)
        assert results == (True, [nic_to_delete.to_ansible()], [None])


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
        results = new_nic.is_update_needed(existing_nic)
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
        results = new_nic.is_update_needed(existing_nic)
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
        results = new_nic.is_update_needed(existing_nic)
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
        results = new_nic.is_update_needed(existing_nic)
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
        results = new_nic.is_update_needed(existing_nic)
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
        results = new_nic.is_update_needed(existing_nic)
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
        results = new_nic.is_update_needed(existing_nic)
        assert results is False


class TestUpdateNic:
    def test_update_nic_when_one_nic_updated(self, rest_client):
        before = []
        after = []
        new_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "vlan_new": 3,
            "macAddress": "12:34:56:78:AB",
            "connected": True,
            "type": "virtio",
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        existing_nic = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "macAddress": "12:34:56:78:AB",
            "connected": True,
            "type": "virtio",
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
        }
        new_nic_obj = Nic.from_hypercore(hypercore_data=new_nic)
        existing_nic_obj = Nic.from_hypercore(hypercore_data=existing_nic)
        new_nic_data = new_nic_obj.to_ansible()
        existing_nic_data = existing_nic_obj.to_ansible()
        rest_client.update_record.return_value = {"taskTag": "1234"}
        rest_client.get_record.return_value = new_nic
        before.append(existing_nic_data)
        after.append(new_nic_data)
        changed = True
        results = Nic.send_update_nic_request_to_hypercore(
            rest_client, new_nic_obj, existing_nic_obj, before, after
        )
        assert results == (changed, before, after)
