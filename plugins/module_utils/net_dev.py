# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from .errors import MissingValue


class NetDev:
    def __init__(self, client=None, net_dev_dict=None):
        self.client = client
        if net_dev_dict:
            self.deserialize(net_dev_dict)


    def __eq__(self, other):
        return (self.vlan == other.vlan and self.vlan_new == other.vlan_new and 
                self.net_dev_type == other.net_dev_type and self.connected == other.connected and 
                self.uuid == other.uuid and self.mac == other.mac)

    # Compare two Network interfaces
    @classmethod
    def compare(cls, old_net_dev, new_net_dev):
        if (new_net_dev == old_net_dev):
            return True
        return False


    # Primarily used for vm_info and vm_nic_info | should return info that user can copy paste to create new netowrk interface
    @classmethod
    def create_network_interface_info_list(cls, network_interface_data_list):
        network_interface_info_list = []
        for network_interface in network_interface_data_list:
            virtual_machine_net_dev_info_dict = {}
            virtual_machine_net_dev_info_dict["uuid"] = network_interface.uuid
            virtual_machine_net_dev_info_dict["vlan"] = network_interface.vlan
            virtual_machine_net_dev_info_dict["type"] = network_interface.net_dev_type
            virtual_machine_net_dev_info_dict["mac"] = network_interface.mac
            virtual_machine_net_dev_info_dict["connected"] = network_interface.connected
            virtual_machine_net_dev_info_dict["ipv4Addresses"] = network_interface.ipv4Addresses
            network_interface_info_list.append(virtual_machine_net_dev_info_dict)
        return network_interface_info_list

    # Pack object into dictionary, ready to be sent
    def serialize(self):
        net_dev_dict = {}
        net_dev_dict["vlan"] = self.vlan
        if self.vlan_new: # if not None, vlan_new is used
            net_dev_dict["vlan"] = self.vlan_new
        if self.net_dev_type:
            net_dev_dict["type"] = self.net_dev_type.upper()
        if self.connected:
            net_dev_dict["connected"] = self.connected
        net_dev_dict["virDomainUUID"] = self.vm_uuid
        if self.mac: # if it's empty we don't send, it auto-generates
            net_dev_dict["macAddress"] = self.mac
        return net_dev_dict


    def deserialize(self, net_dev_dict):
        self.vlan = net_dev_dict.get("vlan", 0)
        self.vlan_new = net_dev_dict.get("vlan_new", None)
        self.net_dev_type = net_dev_dict.get("type", "").upper()
        self.connected = net_dev_dict.get("connected", True)
        self.vm_uuid = net_dev_dict.get("vm_uuid", "")
        self.uuid = net_dev_dict.get("uuid", "")
        self.mac = net_dev_dict.get("mac", net_dev_dict.get("macAddress", "")) # mac is from playbook, macAddress is from API
        self.ipv4Addresses = net_dev_dict.get("ipv4Addresses", [])
