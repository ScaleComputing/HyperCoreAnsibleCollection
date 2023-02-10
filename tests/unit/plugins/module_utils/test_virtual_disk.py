# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from copy import deepcopy

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.virtual_disk import (
    VirtualDisk,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires2.7 or higher"
)


class TestVirtualDisk:
    def setup_method(self):
        self.virtual_disk = VirtualDisk(
            name="vdisk-0",
            uuid="vdisk-uuid",
            block_size=1048576,
            size=104857600,
            replication_factor=2,
        )
        self.from_hypercore_dict = dict(
            blockSize=1048576,
            capacityBytes=104857600,
            name="vdisk-0",
            replicationFactor=2,
            totalAllocationBytes=10485760,
            uuid="vdisk-uuid",
        )
        # self.to_hypercore_dict = dict(
        #     name="vdisk-0",
        #     uuid="vdisk-uuid",
        #     block_size=1048576,
        #     size=104857600,
        #     replication_factor=2,
        # )
        self.to_ansible_dict = dict(
            name="vdisk-0",
            uuid="vdisk-uuid",
            block_size=1048576,
            size=104857600,
            replication_factor=2,
        )

    def test_virtual_disk_to_hypercore(self):
        with pytest.raises(NotImplementedError):
            self.virtual_disk.to_hypercore()

    def test_virtual_disk_from_hypercore_dict_not_empty(self):
        virtual_disk_from_hypercore = VirtualDisk.from_hypercore(
            self.from_hypercore_dict
        )
        assert self.virtual_disk == virtual_disk_from_hypercore

    # def test_virtual_disk_from_hypercore_dict_empty(self):
    #     assert VirtualDisk.from_hypercore({}) is None

    def test_virtual_disk_to_ansible(self):
        print(self.virtual_disk.to_ansible())
        assert self.virtual_disk.to_ansible() == self.to_ansible_dict

    def test_virtual_disk_from_ansible(self):
        virtual_disk_from_ansible = VirtualDisk.from_ansible(self.from_hypercore_dict)
        assert "vdisk-0" == virtual_disk_from_ansible.name
        assert virtual_disk_from_ansible.uuid is None
        assert virtual_disk_from_ansible.block_size is None
        assert virtual_disk_from_ansible.size is None
        assert virtual_disk_from_ansible.replication_factor is None

    def test_get_state(self, rest_client):
        query = dict()
        rest_client.list_records.return_value = [self.from_hypercore_dict]

        result = VirtualDisk.get_state(rest_client, query)
        print(result)
        assert result == [
            {
                "name": "vdisk-0",
                "uuid": "vdisk-uuid",
                "block_size": 1048576,
                "size": 104857600,
                "replication_factor": 2,
            }
        ]

    def test_get_state_more_than_one_record(self, rest_client):
        expected_result = [
            {
                "name": "vdisk-0",
                "uuid": "vdisk-uuid",
                "block_size": 1048576,
                "size": 104857600,
                "replication_factor": 2,
            },
            {
                "name": "vdisk-1",
                "uuid": "vdisk-uuid-1",
                "block_size": 1048576,
                "size": 104857600,
                "replication_factor": 2,
            },
        ]
        hypercore_dict_0 = deepcopy(self.from_hypercore_dict)
        hypercore_dict_1 = deepcopy(self.from_hypercore_dict)
        hypercore_dict_1.update(
            {
                "name": "vdisk-1",
                "uuid": "vdisk-uuid-1",
            }
        )
        query = dict()
        rest_client.list_records.return_value = [
            hypercore_dict_0,
            hypercore_dict_1,
        ]
        result = VirtualDisk.get_state(rest_client, query)
        assert expected_result == result

    def test_get_state_no_record(self, rest_client):
        query = dict()
        rest_client.list_records.return_value = []

        result = VirtualDisk.get_state(rest_client, query)
        assert result == []
