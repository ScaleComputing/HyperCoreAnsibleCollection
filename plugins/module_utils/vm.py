# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.errors import DeviceNotUnique
from ..module_utils.nic import Nic
from ..module_utils.disk import Disk
from ..module_utils.utils import PayloadMapper
from ..module_utils.rest_client import RestClient
from ..module_utils.utils import filter_dict, transform_ansible_to_hypercore_query

FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE = dict(
    started="RUNNING",
    stopped="SHUTOFF",
)

# Inverted dict FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE
FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE = {
    v: k for k, v in FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE.items()
}


class VM(PayloadMapper):
    # Fields cloudInitData, desiredDisposition and latestTaskTag are left out and won't be transferred between
    # ansible and hypercore transformations
    # power_state inside VM holds ansible-native value (meaning, it can take either started or stopped).
    def __init__(
        self,
        name,
        memory,
        vcpu,
        uuid=None,
        tags=None,  # tags are stored internally as list of strings
        description=None,
        power_state=None,
        nics=None,  # nics represents a list of type Nic
        disks=None,  # disks represents a list of type Nic
        boot_devices=None,
        attach_guest_tools_iso=False,
        operating_system=None,
    ):

        self.operating_system = operating_system
        self.uuid = uuid
        self.name = name
        self.tags = tags
        self.description = description
        self.mem = memory
        self.power_state = power_state
        self.numVCPU = vcpu
        self.nics = nics or []
        self.disks = disks or []
        self.boot_devices = boot_devices or []
        self.attach_guest_tools_iso = attach_guest_tools_iso

    @classmethod
    def from_ansible(cls, vm_dict):
        return VM(
            uuid=vm_dict.get("uuid", None),  # No uuid when creating object from ansible
            name=vm_dict["vm_name"],
            tags=vm_dict["tags"],
            description=vm_dict["description"],
            memory=vm_dict["memory"],
            vcpu=vm_dict["vcpu"],
            nics=[
                Nic.create_from_ansible(nic_dict=nic) for nic in vm_dict["nics"] or []
            ],
            disks=[
                Disk(from_hc3=True, disk_dict=disk) for disk in vm_dict["disks"] or []
            ],
            boot_devices=vm_dict.get("boot_devices", []),
            attach_guest_tools_iso=vm_dict["attach_guest_tools_iso"] or False,
            operating_system=None,
            power_state=vm_dict.get("power_state", None),
        )

    @classmethod
    def from_hypercore(cls, vm_dict):
        if (
            vm_dict is None
        ):  # In case we call RestClient.get_record and there is no results
            return None
        return VM(
            uuid=vm_dict["uuid"],  # No uuid when creating object from ansible
            name=vm_dict["name"],
            tags=vm_dict["tags"].split(","),
            description=vm_dict["description"],
            memory=vm_dict["mem"],
            power_state=FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE[vm_dict["state"]],
            vcpu=vm_dict["numVCPU"],
            nics=[Nic.create_from_hc3(nic_dict=nic) for nic in vm_dict["netDevs"]],
            disks=[
                Disk(from_hc3=True, disk_dict=disk) for disk in vm_dict["blockDevs"]
            ],
            # TODO: When boot devices get implemented, add transformation here
            boot_devices=vm_dict["bootDevices"],
            attach_guest_tools_iso=vm_dict.get("attachGuestToolsISO", ""),
            operating_system=vm_dict["operatingSystem"],
        )

    def to_hypercore(self):
        vm_dict = dict(
            name=self.name,
            description=self.description,
            mem=self.mem,
            numVCPU=self.numVCPU,
            blockDevs=[disk.data_to_hc3() for disk in self.disk_list],
            netDevs=[nic.data_to_hc3() for nic in self.nic_list],
            # TODO: When boot devices get implemented, add transformation here
            bootDevices=self.boot_devices,
            tags=",".join(self.tags),
            uuid=self.uuid,
            attachGuestToolsISO=self.attach_guest_tools_iso,
        )
        if self.operating_system:
            vm_dict["operatingSystem"] = self.operating_system
        # state attribute is used by HC3 only during VM create.
        if self.power_state:
            vm_dict["state"] = FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE[self.power_state]
        return vm_dict

    def to_ansible(self):
        # state attribute is used by HC3 only during VM create.
        return dict(
            vm_name=self.name,
            description=self.description,
            operating_system=self.operating_system,
            power_state=self.power_state,
            memory=self.mem,
            vcpu=self.numVCPU,
            disks=[disk.data_to_ansible() for disk in self.disk_list],
            nics=[nic.data_to_ansible() for nic in self.nic_list],
            tags=self.tags,
            uuid=self.uuid,
            boot_devices=self.boot_devices,
            attach_guest_tools_iso=self.attach_guest_tools_iso,
        )

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
            return None
        all_macs = [nic.mac for nic in self.nic_list]
        # TODO raise specific exception
        if all_macs.count(mac) > 1:
            raise DeviceNotUnique("nic - vm.py - find_nic()")
        for nic in self.nic_list:
            if nic.mac == mac:
                return nic

    def find_disk(self, slot):
        # TODO we need to find by (name, disk_type, disk_slot).
        all_slots = [disk.slot for disk in self.disk_list]
        if all_slots.count(slot) > 1:
            raise DeviceNotUnique("disk - vm.py - find_disk()")
        for disk in self.disk_list:
            if disk.slot == slot:
                return disk

    def create_payload_to_hc3(self):
        dom = self.to_hypercore()
        del dom["uuid"]  # No uuid is used when creating payload
        return dict(
            options=dict(attachGuestToolsISO=dom.pop("attachGuestToolsISO")),
            dom=dom,
        )

    def update_payload_to_hc3(self):
        update_body = self.to_hypercore()
        update_body.pop("attachGuestToolsISO")
        return update_body

    @property
    def nic_list(self):
        return self.nics

    @property
    def disk_list(self):
        return self.disks

    def __eq__(self, other):
        """One VM is equal to another if it has ALL attributes exactly the same"""
        return all(
            (
                self.operating_system == other.operating_system,
                self.uuid == other.uuid,
                self.name == other.name,
                self.tags == other.tags,
                self.description == other.description,
                self.mem == other.mem,
                self.power_state == other.power_state,
                self.numVCPU == other.numVCPU,
                self.nics == other.nics,
                self.disks == other.disks,
                self.boot_devices == other.boot_devices,
                self.attach_guest_tools_iso == other.attach_guest_tools_iso,
            )
        )

    def __str__(self):
        return super().__str__()

    @classmethod
    def compare(cls, ansible_dict, hypercore_dict):
        """
        :param ansible_dict: Dict that is defined by user in playbook (often referred as module.params in code)
        :param hypercore_dict: Dict that is obtained from HyperCore API
        :return: Bool value if those dict represent the same objects in python
        """
        return VM.from_hypercore(vm_dict=hypercore_dict) == VM.from_ansible(
            vm_dict=ansible_dict
        )

    @classmethod
    def get(cls, query, rest_client):  # if query is None, return list of all VMs
        record = rest_client.list_records(
            "/rest/v1/VirDomain",
            query,
        )
        if not record:
            return []
        return [
            VM.from_hypercore(vm_dict=virtual_machine) for virtual_machine in record
        ]

    # TODO (domen): Remove usages of get_legacy method with method get
    @classmethod
    def get_legacy(
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

    @classmethod
    def get_by_name(cls, ansible_dict, rest_client):
        """
        With given dict from playbook, finds the existing vm by name from the HyperCore api and constructs object VM if
        the record exists. If there is no record with such name, None is returned.
        """
        ansible_query = filter_dict(ansible_dict, "vm_name")
        hypercore_query = transform_ansible_to_hypercore_query(
            ansible_query, dict(vm_name="name")
        )
        hypercore_dict = rest_client.get_record(
            "/rest/v1/VirDomain", hypercore_query, must_exist=False
        )
        vm_from_hypercore = VM.from_hypercore(hypercore_dict)
        return vm_from_hypercore
