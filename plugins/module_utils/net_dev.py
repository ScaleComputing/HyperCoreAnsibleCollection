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
        return (self.vlan == other.vlan and self.new_vlan == other.new_vlan and 
                self.net_dev_type == other.net_dev_type and self.connected == other.connected and 
                self.uuid == other.uuid and self.macAddress == other.macAddress)

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
        try:
            for network_interface in network_interface_data_list:
                virtual_machine_net_dev_info_dict = {}
                virtual_machine_net_dev_info_dict["uuid"] = network_interface.uuid
                virtual_machine_net_dev_info_dict["vlan"] = network_interface.vlan
                virtual_machine_net_dev_info_dict["type"] = network_interface.net_dev_type
                virtual_machine_net_dev_info_dict["macAddress"] = network_interface.macAddress
                virtual_machine_net_dev_info_dict["connected"] = network_interface.connected
                virtual_machine_net_dev_info_dict["ipv4Addresses"] = network_interface.ipv4Addresses
                network_interface_info_list.append(virtual_machine_net_dev_info_dict)
        except KeyError:
            raise MissingValue("in network interface dictionary - nic.py - (create_network_interface_info_list)")
        return network_interface_info_list

    # Pack object into dictionary, ready to be sent
    def serialize(self):
        net_dev_dict = {}
        net_dev_dict["vlan"] = self.vlan
        if self.new_vlan:
            net_dev_dict["new_vlan"] = self.new_vlan
        net_dev_dict["type"] = self.net_dev_type.upper()
        net_dev_dict["connected"] = self.connected
        net_dev_dict["virDomainUUID"] = self.vm_uuid
        if self.macAddress: # if it's empty we don't send, so it auto-generates
            net_dev_dict["macAddress"] = self.macAddress
        return net_dev_dict


    def deserialize(self, net_dev_dict):
        self.vlan = net_dev_dict.get("vlan", 0)
        self.new_vlan = net_dev_dict.get("new_vlan", None)
        self.net_dev_type = net_dev_dict.get("type", "").upper()
        self.connected = net_dev_dict.get("connected", True)
        self.vm_uuid = net_dev_dict.get("vm_uuid", "")
        self.uuid = net_dev_dict.get("uuid", "")
        self.macAddress = net_dev_dict.get("macAddress", "")
        self.ipv4Addresses = net_dev_dict.get("ipv4Addresses", [])
