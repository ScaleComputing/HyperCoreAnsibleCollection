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
        nic = Nic.create_from_ansible(ansible_data)
        assert 10 == nic.vlan
        assert "virtio" == nic.type  # TODO fix, use enum
        assert "12:00:00:00:00:00" == nic.mac
        # ATM ansible module does not allow setting connected flag
        assert nic.connected is None
        assert [] == nic.ipv4Addresses

    @classmethod
    def _get_nic_from_hc3(cls):
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
        return Nic.create_from_hc3(hc3_data)

    def test_init_from_hc3_data(self):
        nic = self._get_nic_from_hc3()
        assert "my-nic-uuid" == nic.uuid
        assert 10 == nic.vlan
        assert "virtio" == nic.type
        assert "12:00:00:00:00:00" == nic.mac
        assert nic.connected is True
        assert ["10.0.0.10", "10.0.1.10"] == nic.ipv4Addresses

    def test_to_ansible(self):
        nic = self._get_nic_from_hc3()
        ansible_data = nic.data_to_ansible()
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
