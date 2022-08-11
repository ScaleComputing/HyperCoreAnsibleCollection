# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.errors import DeviceNotUnique
from ..module_utils.nic import Nic
from ..module_utils.disk import Disk
from ..module_utils.rest_client import RestClient


class VM:
    def __init__(self, from_hc3, vm_dict, client=None):
        # TODO simplify this __init__, add two classmethods create_from_hc3(data) and create_from_ansible(data)
        # The data_from_hc3 is almost that thing.
        # See also Nic class.
        self.client = client
        if from_hc3:
            self.data_from_hc3(vm_dict)
        else:
            self.data_from_ansible(vm_dict)

    @property
    def nic_list(self):
        return self._nic_list

    @property
    def disk_list(self):
        return self._disk_list

    @classmethod
    def get(
        cls, client, name=None, uuid=None
    ):  # get all VMs or specific (requires parameter Name or uuid)
        rest_client = RestClient(client=client)
        end_point = "/rest/v1/VirDomain/"
        all_vms_list = rest_client.list_records(endpoint=end_point)
        if name:
            all_vm_names = [vm["name"] for vm in all_vms_list]
            # TODO raise specific exception if multiple VMs have same name
            if all_vm_names.count(name) > 1:
                raise DeviceNotUnique("Virtual machine - vm.py - get()")
            for (
                vm
            ) in (
                all_vms_list
            ):  # find first | what if more than one VM with the same name?
                if vm["name"] == name:
                    return [vm]
            return []
        elif uuid:
            for vm in all_vms_list:
                if vm["uuid"] == uuid:
                    return [vm]
            return []
        return all_vms_list

    # from hc3
    def data_from_ansible(self, vm_dict):
        # set to None also attributes that are newer set via ansible module
        # TODO those should be set to None/"" in __init__
        self.operating_system = None
        self.desired_disposition = None
        self.latest_task_tag = None

        # TODO For mandatory parameters [] can be used.
        self.uuid = vm_dict.get("uuid", "")
        self.name = vm_dict.get("vm_name", "")
        self.tags = []
        if "tags" in vm_dict.keys() and vm_dict["tags"]:
            for tag in vm_dict["tags"]:
                self.tags.append(tag)
        self.description = vm_dict.get("description", "")
        self.mem = vm_dict.get("memory", 0)
        self.power_state = vm_dict.get("power_state", "")
        self.numVCPU = vm_dict.get("vcpu", 0)
        self._disk_list = []
        self._nic_list = []
        self.operating_system = vm_dict.get("operatingSystem", None)
        if "disks" in vm_dict.keys() and vm_dict["disks"]:
            for disk in vm_dict["disks"]:
                self.disk_list.append(Disk(from_hc3=True, disk_dict=disk))
        if "nics" in vm_dict.keys() and vm_dict["nics"]:
            for nic in vm_dict["nics"]:
                self.nic_list.append(Nic.create_from_ansible(nic_dict=nic))
        self.bootDevices = vm_dict.get("boot_devices", [])
        # TODO cloud_init_data userData/metaData will be provided as a dict.
        # Also, only one might be provided (corner cases...).
        # TODO Update this part fo code.
        self.cloud_init_data = vm_dict.get(
            "cloudInitData", {"userData": {}, "metaData": {}}
        )
        self.attach_guest_tools_iso = vm_dict.get("attachGuestToolsISO", False)

    def data_from_hc3(self, vm_dict):
        # TODO For always-present field [] can be used.
        self.uuid = vm_dict.get("uuid", "")
        self.name = vm_dict.get("name", "")
        self.description = vm_dict.get("description", "")
        self.operating_system = vm_dict.get("operatingSystem", "")
        self.power_state = vm_dict.get("state", "")
        self.desired_disposition = vm_dict.get("desiredDisposition", "")
        self.console = vm_dict.get("console", {})
        self.mem = vm_dict.get("mem", 0)
        self.numVCPU = vm_dict.get("numVCPU", 0)
        self._disk_list = []
        self._nic_list = []
        for disk in vm_dict["blockDevs"]:
            self.disk_list.append(Disk(from_hc3=True, disk_dict=disk))
        for nic in vm_dict["netDevs"]:
            self.nic_list.append(Nic.create_from_hc3(nic_dict=nic))
        self.stats = vm_dict["stats"]
        self.latest_task_tag = vm_dict.get("latestTaskTag", {})
        self.tags = []
        for tag in vm_dict["tags"].split(","):
            self.tags.append(tag)
        self.bootDevices = vm_dict.get("bootDevices", [])
        # TODO cloud_init_data userData/metaData will be provided as a dict.
        # Also, only one might be provided (corner cases...).
        # TODO Update this part fo code.
        self.cloud_init_data = vm_dict.get(
            "cloudInitData", {"userData": {}, "metaData": {}}
        )
        self.attach_guest_tools_iso = vm_dict.get("attachGuestToolsISO", False)

    def data_to_hc3(self):
        vm_dict = {
            "name": self.name,
            "description": self.description,
            "mem": self.mem,
            "numVCPU": self.numVCPU,
            "blockDevs": [disk.data_to_hc3() for disk in self.disk_list],
            "netDevs": [nic.data_to_hc3() for nic in self.nic_list],
            "tags": ",".join(self.tags),
            "uuid": self.uuid,
            # TODO bootDevices for HC3 should be a list of UUIDs (I think)
            # If new VM is created, we can get those UUIDs only after VM is created.
            # "bootDevices": self.bootDevices,
            # TODO userData and metaData for HC3 must be base64 encoded yaml content
            # vm_dict["cloudInitData"] = self.cloud_init_data
            "attachGuestToolsISO": self.attach_guest_tools_iso,
        }
        if self.operating_system:
            vm_dict["operatingSystem"] = self.operating_system
        # state attribute is used by HC3 only during VM create.
        if self.power_state:
            vm_dict["state"] = self.power_state.upper()
        return vm_dict

    def data_to_ansible(self):
        vm_dict = {
            "name": self.name,
            "description": self.description,
            "operatingSystem": self.operating_system,
            # state attribute is used by HC3 only during VM create.
            "power_state": self.power_state.upper(),
            "memory": self.mem,
            "vcpu": self.numVCPU,
            "disks": [disk.data_to_ansible() for disk in self.disk_list],
            "nics": [nic.data_to_ansible() for nic in self.nic_list],
            "tags": ",".join(self.tags),
            "uuid": self.uuid,
            "boot_devices": self.bootDevices,
            # TODO userData and metaData for HC3 must be base64 encoded yaml content
            # vm_dict["cloudInitData"] = self.cloud_init_data
            "attachGuestToolsISO": self.attach_guest_tools_iso,
        }
        return vm_dict

    # search by vlan or mac as specified in US-11:
    # (https://gitlab.xlab.si/scale-ansible-collection/scale-ansible-collection-docs/-/blob/develop/docs/user-stories/us11-manage-vnics.md)
    def find_nic(self, vlan=None, mac=None):
        if vlan:
            all_vlans = [nic.vlan for nic in self.nic_list]
            # TODO raise specific exception
            if all_vlans.count(vlan) > 1:
                raise DeviceNotUnique("nic - vm.py - find_nic()")
            for nic in self.nic_list:
                if nic.vlan == vlan:
                    return nic
        else:
            all_macs = [nic.mac for nic in self.nic_list]
            # TODO raise specific exception
            if all_macs.count(mac) > 1:
                raise DeviceNotUnique("nic - vm.py - find_nic()")
            for nic in self.nic_list:
                if nic.mac == mac:
                    return nic

    def find_disk(self, slot):
        # TODO we need to find by (vm_name, disk_type, disk_slot).
        all_slots = [disk.slot for disk in self.disk_list]
        if all_slots.count(slot) > 1:
            raise DeviceNotUnique("disk - vm.py - find_disk()")
        for disk in self.disk_list:
            if disk.slot == slot:
                return disk
