# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ..module_utils.errors import MissingValue
from ..module_utils.net_dev import NetDev
from ..module_utils.block_dev import BlockDev

class VM:
    def __init__(self, client=None, vm_dict=None):
        self.client = client
        if vm_dict:
            self.deserialize(vm_dict)


    @property
    def net_devs_list(self):
        return self._net_devs_list


    @property
    def block_devs_list(self):
        return self._block_devs_list


    @classmethod
    def get(cls, client, name=None, uuid=None): # get all VMs or specific (requires parameter Name or uuid)
        end_point = "/rest/v1/VirDomain/"
        all_vms_list = client.request("GET", end_point).json
        if name:
            all_vm_names = [vm["name"] for vm in all_vms_list]
            # TODO raise specific exception if multiple VMs have same name
            assert all_vm_names.count(name) <= 1
            for vm in all_vms_list: # find first | what if more than one VM with the same name?
                if vm["name"] == name:
                    return [vm]
            return []
        elif uuid:
            for vm in all_vms_list:
                if vm["uuid"] == uuid:
                    return [vm]
            return []
        return all_vms_list


    # Primarily used for vm_info | should return info that user can copy paste to create new VM
    @classmethod
    def create_vm_info(cls, virtual_machine_info_dict):
        necessary_virtual_machine_info_dict = {}
        try:
            necessary_virtual_machine_info_dict["uuid"] = virtual_machine_info_dict["uuid"]
            necessary_virtual_machine_info_dict["name"] = virtual_machine_info_dict["name"]
            necessary_virtual_machine_info_dict["description"] = virtual_machine_info_dict["description"]
            necessary_virtual_machine_info_dict["memory"] = virtual_machine_info_dict["mem"]
            necessary_virtual_machine_info_dict["power_state"] = virtual_machine_info_dict["state"]
            necessary_virtual_machine_info_dict["vcpu"] = virtual_machine_info_dict["numVCPU"]
            necessary_virtual_machine_info_dict["tags"] = virtual_machine_info_dict["tags"]
            necessary_virtual_machine_info_dict["disks"] = virtual_machine_info_dict["blockDevs"]
            necessary_virtual_machine_info_dict["nics"] = virtual_machine_info_dict["netDevs"]
            necessary_virtual_machine_info_dict["boot_devices"] = virtual_machine_info_dict["bootDevices"]
        except KeyError:
            raise MissingValue("in virtual machine info dictionary - vm.py - (create_vm_info)")
        return necessary_virtual_machine_info_dict

    # Primarily used for vm_info | should return complete info that user can copy paste to create new VM
    def create_vm_info_list(self, virtual_machine_list=None):
        virtual_machines_info_list = []
        if virtual_machine_list: # In case user wants a list of all VMs
            for virtual_machine_info_dict in virtual_machine_list:
                virtual_machine_info_dict = VM.create_vm_info(virtual_machine_info_dict)
                virtual_machine_info_dict["disks"] = BlockDev.create_disk_info_list(virtual_machine_info_dict["disks"])
                virtual_machine_info_dict["nics"] = NetDev.create_network_interface_info_list(virtual_machine_info_dict["nics"])
                virtual_machines_info_list.append(virtual_machine_info_dict)
        else: # Otherwise data is taken from the object VM
            virtual_machine_info_dict = self.serialize()
            virtual_machine_info_dict = VM.create_vm_info(virtual_machine_info_dict)
            virtual_machine_info_dict["disks"] = BlockDev.create_disk_info_list(self.block_devs_list)
            virtual_machine_info_dict["nics"] = NetDev.create_network_interface_info_list(self.net_devs_list)
            virtual_machines_info_list.append(virtual_machine_info_dict)
        return virtual_machines_info_list


    def deserialize(self, vm_dict):
        self.name = vm_dict.get("name", "")
        self.tags = []
        if "tags" in vm_dict.keys() and vm_dict["tags"]:
            if type(vm_dict["tags"]) == str:
                for tag in vm_dict["tags"].split(","):
                    self.tags.append(tag)
            else:
                for tag in vm_dict["tags"]:
                    self.tags.append(tag)
        self.uuid = vm_dict.get("uuid", "")
        self.description = vm_dict.get("description", "")
        self.mem = vm_dict.get("mem", 0)
        self.power_state = vm_dict.get("power_state", "")
        self.numVCPU = vm_dict.get("numVCPU", 0)
        self._block_devs_list = []
        self._net_devs_list = []
        if "blockDevs" in vm_dict.keys() and vm_dict["blockDevs"]:
            for block_dev in vm_dict["blockDevs"]:
                self.block_devs_list.append(BlockDev(block_dev_dict=block_dev))
        if "netDevs" in vm_dict.keys() and vm_dict["netDevs"]:
            for net_dev in vm_dict["netDevs"]:
                self.net_devs_list.append(NetDev(net_dev_dict=net_dev))
        self.bootDevices = vm_dict.get("bootDevices", [])
        # TODO cloud_init_data userData/metaData will be provided as a dict.
        # Also, only one might be provided (corner cases...).
        # TODO Update this part fo code.
        self.cloud_init_data = vm_dict.get("cloudInitData", {"userData": {}, "metaData": {}})
        self.attach_guest_tools_iso = vm_dict.get("attachGuestToolsISO", False)



    def serialize(self):
        vm_dict = {}
        vm_dict["name"] = self.name
        vm_dict["tags"] = ",".join(self.tags)
        vm_dict["uuid"] = self.uuid
        vm_dict["description"] = self.description
        vm_dict["mem"] = self.mem
        # state attribute is used by HC3 only during VM create.
        vm_dict["state"] = self.power_state.upper()
        vm_dict["numVCPU"] = self.numVCPU
        vm_dict["blockDevs"] = self.block_devs_list
        vm_dict["netDevs"] = self.net_devs_list
        vm_dict["bootDevices"] = self.bootDevices
        # TODO userData and metaData for HC3 must be base64 encoded yaml content
        # vm_dict["cloudInitData"] = self.cloud_init_data
        vm_dict["attachGuestToolsISO"] = self.attach_guest_tools_iso
        return vm_dict


    def find_net_dev(self, vlan):
        all_vlans = [nic.vlan for nic in self.net_devs_list]
        # TODO raise specific exception
        assert all_vlans.count(vlan) <= 1
        for net_dev in self.net_devs_list:
            if net_dev.vlan == vlan:
                return net_dev


    def find_block_dev(self, slot):
        # TODO we need to find by (vm_name, disk_type, disk_slot).
        all_slots = [disk.slot for disk in self.block_devs_list]
        # TODO raise specific exception
        assert all_slots.count(slot) <= 1
        for block_dev in self.block_devs_list:
            if block_dev.slot == slot:
                return block_dev