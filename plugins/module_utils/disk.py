# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Disk:
    def __init__(self, from_hc3, disk_dict, client=None):
        # TODO simplify this __init__, add two classmethods create_from_hc3(data) and create_from_ansible(data)
        # The data_from_hc3 is almost that thing.
        # See also Nic class.
        self.client = client
        if from_hc3:
            self.data_from_hc3(disk_dict)
        else:
            self.data_from_ansible(disk_dict)

    def data_to_hc3(self):
        disk = {
            "uuid": self.uuid,
            "slot": self.slot,
            "name": self.name,
            "size": self.size,
            "type": self.type,
        }
        return disk

    def data_to_ansible(self):
        disk_info_dict = {
            "uuid": self.uuid,
            "disk_slot": self.slot,
            "size": self.size,
            "type": self.type,
        }
        return disk_info_dict

    # Parsing data from API
    def data_from_hc3(self, disk_dict):
        # UUID must be always presnt in HC3 output. Use [], fail if uuid is missing.
        # Similar for other fields.
        # Maybe: raise specific exception from errors.py (MissingValuesHC3).
        self.uuid = disk_dict.get("uuid", "")
        self.slot = disk_dict.get("slot", 0)
        self.name = disk_dict.get("name", "")
        self.size = disk_dict.get("size", 0)
        self.type = disk_dict.get("type", "")

    # Parsing data from ansible input
    def data_from_ansible(self, disk_dict):
        # TODO maybe use None for missing values, not 0 or ""
        # TODO data_from_ansible also has some fields that are mandatory (disk_slot), and [] can be used.
        self.uuid = disk_dict.get("uuid", "")
        self.slot = disk_dict.get("disk_slot", 0)  # TODO disk_dict["disk_slot"]
        self.size = disk_dict.get("size", 0)
        # TODO is type mandatory in ansible playbook?
        self.type = disk_dict.get("type", "")
