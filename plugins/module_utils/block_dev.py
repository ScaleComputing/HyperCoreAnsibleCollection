# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ..module_utils.errors import MissingValue


class BlockDev:
    def __init__(self, client=None, block_dev_dict=None):
        self.client = client
        if block_dev_dict:
            self.deserialize(block_dev_dict)

    # Primarily used for vm_info | should return info that user can copy paste to create new block device
    @classmethod
    def create_disk_info_list(cls, block_dev_list):
        disk_info_list = []
        try:
            for block_dev in block_dev_list:
                virtual_machine_disk_info_dict = {}
                virtual_machine_disk_info_dict["uuid"] = block_dev.uuid
                virtual_machine_disk_info_dict["disk_slot"] = block_dev.slot
                virtual_machine_disk_info_dict["name"] = block_dev.name
                virtual_machine_disk_info_dict["size"] = block_dev.size
                virtual_machine_disk_info_dict["type"] = block_dev.block_dev_type
                disk_info_list.append(virtual_machine_disk_info_dict)
        except KeyError:
            raise MissingValue(
                "in block devices list - block_dev.py - (create_disk_info_list)"
            )
        return disk_info_list

    def serialize(self):
        block_dev_dict = {}
        block_dev_dict["uuid"] = self.uuid
        block_dev_dict["slot"] = self.slot
        block_dev_dict["name"] = self.name
        block_dev_dict["size"] = self.size
        block_dev_dict["block_dev_type"] = self.block_dev_type
        return block_dev_dict

    def deserialize(self, block_dev_dict):
        self.uuid = block_dev_dict.get("uuid", "")
        self.slot = block_dev_dict.get("slot", 0)
        self.name = block_dev_dict.get("name", "")
        self.size = block_dev_dict.get("size", 0)
        self.block_dev_type = block_dev_dict.get("block_dev_type", "")
