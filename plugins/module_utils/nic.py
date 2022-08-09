# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type


class Nic:
    def __init__(self):
        self.uuid = ""
        self.vm_uuid = ""
        self.type = None  # TODO Use Enum
        self.mac = ""
        self.mac_new = None
        self.vlan = None
        self.vlan_new = None
        self.connected = None
        self.ipv4Addresses = []

    def __eq__(self, other):
        return (
            self.vlan == other.vlan
            and self.type == other.type
            and self.connected == other.connected
            and self.uuid == other.uuid
            and self.mac == other.mac
        )

    # Compare two Network interfaces
    @classmethod
    def compare(cls, old_nic, new_nic):
        return new_nic == old_nic

    def data_to_hc3(self):
        nic_dict = {
            "vlan": self.vlan,
            "virDomainUUID": self.vm_uuid,
        }
        # TODO corner case: change vlan 0 -> 10, 10 -> 0. integration test
        if self.vlan_new is not None:
            nic_dict["vlan"] = self.vlan_new
        if self.type:
            nic_dict["type"] = self.type.upper()  # TODO enum
        if self.connected is not None:
            nic_dict["connected"] = self.connected
        # TODO corner case: module is called without mac, with mac_new.
        # It is desired to change MAC to the mac_new, right?
        if self.mac:  # if it's empty we don't send, it auto-generates
            if self.mac_new:  # user wants to change mac address
                nic_dict["macAddress"] = self.mac_new
            else:
                nic_dict["macAddress"] = self.mac
        return nic_dict

    def data_to_ansible(self):
        nic_info_dict = {
            "uuid": self.uuid,
            "vlan": self.vlan,
            "type": self.type,
            "mac": self.mac,
            "connected": self.connected,
            "ipv4_addresses": self.ipv4Addresses,
        }
        return nic_info_dict

    @classmethod
    def create_from_hc3(cls, nic_dict):
        obj = Nic()
        obj.uuid = nic_dict["uuid"]
        # HC3 API GET /VirDomain - we get virDomainUUID for each Nic
        # HC3 API GET /VirDomainNetDevice - virDomainUUID might be empty string
        obj.vm_uuid = nic_dict["virDomainUUID"]
        # TODO fix - INTEL_E1000 -> intel_e1000, RTL. Use Enum
        obj.type = nic_dict["type"].lower()
        obj.mac = nic_dict.get("macAddress", "")
        obj.vlan = nic_dict.get("vlan", 0)
        obj.connected = nic_dict.get("connected", True)
        obj.ipv4Addresses = nic_dict.get("ipv4Addresses", [])
        return obj

    @classmethod
    def create_from_ansible(cls, nic_dict):
        obj = Nic()
        # obj.uuid = nic_dict.get("uuid", "")
        obj.vm_uuid = nic_dict.get("vm_uuid", "")
        obj.type = nic_dict.get("type", "")  # TODO use enum
        obj.mac = nic_dict.get("mac", "")
        obj.mac_new = nic_dict.get("mac_new", None)
        obj.vlan = nic_dict["vlan"]
        obj.vlan_new = nic_dict.get("vlan_new", None)
        # obj.connected = nic_dict.get("connected", None)
        # obj.ipv4Addresses = nic_dict.get("ipv4Addresses", [])
        return obj
