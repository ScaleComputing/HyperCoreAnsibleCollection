# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import base64
from time import sleep, time

from ..module_utils.errors import DeviceNotUnique
from ..module_utils.nic import Nic
from ..module_utils.disk import Disk
from ..module_utils.node import Node
from ..module_utils.iso import ISO
from ..module_utils.utils import (
    PayloadMapper,
    filter_dict,
    transform_query,
    is_superset,
)
from ..module_utils.state import NicState
from ..module_utils.utils import (
    get_query,
    filter_results,
)
from ..module_utils.task_tag import TaskTag
from ..module_utils import errors
from ..module_utils.errors import ScaleComputingError
from ..module_utils.snapshot_schedule import SnapshotSchedule

# FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE and FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE are mappings for how
# states are stored in python/ansible and how are they stored in hypercore

# Inverted dict FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE
FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE = dict(
    RUNNING="started",
    SHUTOFF="stopped",
    BLOCKED="blocked",
    PAUSED="paused",
    SHUTDOWN="shutdown",
    CRASHED="crashed",
)

# FROM_ANSIBLE_TO_HYPERCORE_ACTION_STATE in mapping between how states are stored in ansible and how
# states are stored in hypercore. Used in update_vm_power_state.
FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE = dict(
    start="START",
    shutdown="SHUTDOWN",
    stop="STOP",
    rebot="REBOOT",
    reset="RESET",
    started="START",
)


FROM_ANSIBLE_TO_HYPERCORE_MACHINE_TYPE = {
    "UEFI": "scale-8.10",
    "BIOS": "scale-7.2",
    "vTPM+UEFI": "scale-uefi-tpm-9.2",
}

FROM_HYPERCORE_TO_ANSIBLE_MACHINE_TYPE = {
    v: k for k, v in FROM_ANSIBLE_TO_HYPERCORE_MACHINE_TYPE.items()
}


VM_PAYLOAD_KEYS = [
    "blockDevs",
    "bootDevices",
    "description",
    "machineType",
    "mem",
    "name",
    "netDevs",
    "numVCPU",
    "tags",
    "machineType",
]

VM_DEVICE_QUERY_MAPPING_ANSIBLE = dict(
    disk_slot="disk_slot", nic_vlan="vlan", iso_name="iso_name"
)

DISK_TYPES_HYPERCORE = [
    "IDE_DISK",
    "SCSI_DISK",
    "VIRTIO_DISK",
    "IDE_CDROM",
    "IDE_FLOPPY",
    "NVRAM",
]


REBOOT_LOOKUP = dict(
    vm_name=False,
    description=False,
    tags=False,
    memory=True,
    vcpu=True,
    power_state=False,
    snapshot_schedule=False,
)


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
        node_uuid=None,
        tags=None,  # tags are stored internally as list of strings
        description=None,
        power_state=None,
        nics=None,  # nics represents a list of type Nic
        disks=None,  # disks represents a list of type Nic
        # boot_devices are stored as list of nics and/or disks internally.
        boot_devices=None,
        attach_guest_tools_iso=False,
        operating_system=None,
        node_affinity=None,
        snapshot_schedule=None,
        reboot=False,  # Is reboot needed
        was_shutdown_tried=False,  # Has shutdown request already been tried
        machine_type=None,
    ):

        self.operating_system = operating_system
        self.uuid = uuid
        self.node_uuid = node_uuid
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
        self.node_affinity = node_affinity
        self.snapshot_schedule = snapshot_schedule  # name of the snapshot_schedule
        self.reboot = reboot
        self.was_shutdown_tried = was_shutdown_tried
        self.machine_type = machine_type

    @property
    def nic_list(self):
        return self.nics

    @property
    def disk_list(self):
        return self.disks

    @classmethod
    def from_ansible(cls, vm_dict):
        return cls(
            uuid=vm_dict.get("uuid", None),  # No uuid when creating object from ansible
            name=vm_dict["vm_name"],
            tags=vm_dict["tags"],
            description=vm_dict["description"],
            memory=vm_dict["memory"],
            vcpu=vm_dict["vcpu"],
            nics=[Nic.from_ansible(ansible_data=nic) for nic in vm_dict["nics"] or []],
            disks=[
                Disk.from_ansible(disk_dict) for disk_dict in vm_dict["disks"] or []
            ],
            boot_devices=vm_dict.get("boot_devices", []),
            attach_guest_tools_iso=vm_dict["attach_guest_tools_iso"] or False,
            operating_system=None,
            power_state=vm_dict.get("power_state", None),
            machine_type=vm_dict.get("machine_type", None),
        )

    @classmethod
    def from_hypercore(cls, vm_dict, rest_client):
        # In case we call RestClient.get_record and there is no results
        if vm_dict is None:
            return None

        preferred_node = Node.get_node(
            query={"uuid": vm_dict["affinityStrategy"]["preferredNodeUUID"]},
            rest_client=rest_client,
        )
        backup_node = Node.get_node(
            query={"uuid": vm_dict["affinityStrategy"]["backupNodeUUID"]},
            rest_client=rest_client,
        )

        node_affinity = dict(
            strict_affinity=vm_dict["affinityStrategy"]["strictAffinity"],
            preferred_node=preferred_node.to_ansible()
            if preferred_node
            else dict(
                node_uuid="",
                backplane_ip="",
                lan_ip="",
                peer_id=None,
            ),  # for vm_node_affinity diff check
            backup_node=backup_node.to_ansible()
            if backup_node
            else dict(
                node_uuid="",
                backplane_ip="",
                lan_ip="",
                peer_id=None,
            ),  # for vm_node_affinity diff check,
        )

        snapshot_schedule = SnapshotSchedule.get_snapshot_schedule(
            query={"uuid": vm_dict["snapshotScheduleUUID"]}, rest_client=rest_client
        )

        return cls(
            uuid=vm_dict["uuid"],  # No uuid when creating object from ansible
            node_uuid=vm_dict["nodeUUID"],  # Needed in vm_node_affinity
            name=vm_dict["name"],
            tags=vm_dict["tags"].split(","),
            description=vm_dict["description"],
            memory=vm_dict["mem"],
            power_state=FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE[vm_dict["state"]],
            vcpu=vm_dict["numVCPU"],
            nics=[Nic.from_hypercore(hypercore_data=nic) for nic in vm_dict["netDevs"]],
            disks=[
                Disk.from_hypercore(disk_dict) for disk_dict in vm_dict["blockDevs"]
            ],
            boot_devices=cls.get_vm_device_list(vm_dict),
            attach_guest_tools_iso=vm_dict.get("attachGuestToolsISO", ""),
            operating_system=vm_dict["operatingSystem"],
            node_affinity=node_affinity,
            snapshot_schedule=snapshot_schedule.name
            if snapshot_schedule
            else "",  # "" for vm_params diff check
            machine_type=FROM_HYPERCORE_TO_ANSIBLE_MACHINE_TYPE[vm_dict["machineType"]],
        )

    @classmethod
    def create_cloud_init_payload(cls, ansible_dict):
        if "cloud_init" in ansible_dict.keys() and (
            ansible_dict["cloud_init"]["user_data"]
            or ansible_dict["cloud_init"]["meta_data"]
        ):
            return dict(
                userData=str(
                    base64.b64encode(
                        bytes(str(ansible_dict["cloud_init"]["user_data"]), "utf-8")
                    )
                )[2:-1]
                if ansible_dict["cloud_init"]["user_data"] is not None
                else "",
                metaData=str(
                    base64.b64encode(
                        bytes(str(ansible_dict["cloud_init"]["meta_data"]), "utf-8")
                    )
                )[2:-1]
                if ansible_dict["cloud_init"]["meta_data"] is not None
                else "",
            )
        return None

    @staticmethod
    def create_export_or_import_vm_payload(ansible_dict, cloud_init, is_export):
        key = "target" if is_export else "source"
        payload = {key: {}, "template": {}}
        if not is_export:
            payload["template"]["name"] = ansible_dict["vm_name"]
        if ansible_dict["smb"]:
            # ATM we request path to start with '/'
            pathURI = f"smb://{ansible_dict['smb']['username']}:{ansible_dict['smb']['password']}@{ansible_dict['smb']['server']}{ansible_dict['smb']['path']}"
            payload[key] = {"pathURI": pathURI}
            if ansible_dict["smb"]["file_name"]:
                payload[key]["definitionFileName"] = ansible_dict["smb"]["file_name"]
        elif ansible_dict["http_uri"]:
            payload[key] = {
                "pathURI": ansible_dict["http_uri"]["path"],
                "definitionFileName": ansible_dict["http_uri"]["file_name"],
            }
        if cloud_init:
            payload["template"]["cloudInitData"] = cloud_init
        return payload

    @classmethod
    def create_clone_vm_payload(
        cls, clone_name, ansible_tags, hypercore_tags, cloud_init
    ):
        data = {"template": {}}
        if clone_name:
            data["template"]["name"] = clone_name
        if (
            ansible_tags or hypercore_tags
        ):  # Cloned VM does not retain tags from the original
            for tag in ansible_tags or []:
                if tag not in hypercore_tags:
                    hypercore_tags.append(tag)
            data["template"]["tags"] = ",".join(hypercore_tags)
        if cloud_init:
            data["template"]["cloudInitData"] = cloud_init
        return data

    @classmethod
    def get(cls, query, rest_client):  # if query is None, return list of all VMs
        record = rest_client.list_records(
            "/rest/v1/VirDomain",
            query,
        )
        if not record:
            return []
        return [
            cls.from_hypercore(vm_dict=virtual_machine, rest_client=rest_client)
            for virtual_machine in record
        ]

    @classmethod
    def get_or_fail(cls, query, rest_client):  # if vm is not found, raise exception
        record = rest_client.list_records(
            "/rest/v1/VirDomain",
            query,
        )
        if not record:
            raise errors.VMNotFound(query)
        return [
            cls.from_hypercore(vm_dict=virtual_machine, rest_client=rest_client)
            for virtual_machine in record
        ]

    @classmethod
    def get_by_name(
        cls, ansible_dict, rest_client, must_exist=False, name_field="vm_name"
    ):
        """
        With given dict from playbook, finds the existing vm by name from the HyperCore api and constructs object VM if
        the record exists. If there is no record with such name, None is returned.
        """
        # name_field won't be equal to "vm_name" in case of updating the vm.
        # In that case, it's going to be equal to vm_name_new.
        query = get_query(
            ansible_dict, name_field, ansible_hypercore_map={name_field: "name"}
        )
        hypercore_dict = rest_client.get_record(
            "/rest/v1/VirDomain", query, must_exist=must_exist
        )
        vm_from_hypercore = cls.from_hypercore(hypercore_dict, rest_client)
        return vm_from_hypercore

    @classmethod
    def import_vm(cls, rest_client, ansible_dict):
        cloud_init = cls.create_cloud_init_payload(ansible_dict)
        data = cls.create_export_or_import_vm_payload(
            ansible_dict,
            cloud_init,
            is_export=False,
        )
        return rest_client.create_record(
            endpoint="/rest/v1/VirDomain/import",
            payload=data,
            check_mode=False,
            timeout=None,
        )

    def to_hypercore(self):
        vm_dict = dict(
            name=self.name,
            description=self.description,
            mem=self.mem,
            numVCPU=self.numVCPU,
            blockDevs=[disk.to_hypercore() for disk in self.disk_list],
            netDevs=[nic.to_hypercore() for nic in self.nic_list],
            bootDevices=self.boot_devices,
            tags=",".join(self.tags) if self.tags is not None else "",
            uuid=self.uuid,
            attachGuestToolsISO=self.attach_guest_tools_iso,
        )
        if self.operating_system:
            vm_dict["operatingSystem"] = self.operating_system
        # state attribute is used by HC3 only during VM create.
        if self.power_state:
            vm_dict["state"] = FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE[self.power_state]
        if self.machine_type:
            vm_dict["machineType"] = FROM_ANSIBLE_TO_HYPERCORE_MACHINE_TYPE[
                self.machine_type
            ]
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
            disks=[disk.to_ansible() for disk in self.disk_list],
            nics=[nic.to_ansible() for nic in self.nic_list],
            tags=self.tags,
            uuid=self.uuid,
            boot_devices=[
                boot_device.to_ansible() for boot_device in self.boot_devices
            ],
            attach_guest_tools_iso=self.attach_guest_tools_iso,
            node_affinity=self.node_affinity,
            snapshot_schedule=self.snapshot_schedule,
            machine_type=self.machine_type,
        )

    # search by vlan or mac as specified in US-11:
    # (https://gitlab.xlab.si/scale-ansible-collection/scale-ansible-collection-docs/-/blob/develop/docs/user-stories/us11-manage-vnics.md)
    def find_nic(self, vlan=None, mac=None, vlan_new=None, mac_new=None):
        existing_hypercore_nic_with_new = None
        existing_hypercore_nic = None
        if vlan is not None:
            all_vlans = [nic.vlan for nic in self.nic_list]
            if all_vlans.count(vlan) > 1:
                raise DeviceNotUnique("nic - vm.py - find_nic()")
            for nic in self.nic_list:
                if nic.vlan == vlan:
                    existing_hypercore_nic = nic
                elif vlan_new is not None and nic.vlan == vlan_new:
                    existing_hypercore_nic_with_new = nic
        else:
            all_macs = [nic.mac for nic in self.nic_list]
            if all_macs.count(mac) > 1:
                raise DeviceNotUnique("nic - vm.py - find_nic()")
            for nic in self.nic_list:
                if nic.mac == mac:
                    existing_hypercore_nic = nic
                elif mac_new is not None and nic.mac == mac_new:
                    existing_hypercore_nic_with_new = nic
        return existing_hypercore_nic, existing_hypercore_nic_with_new

    def find_disk(self, slot):
        all_slots = [disk.slot for disk in self.disk_list]
        if all_slots.count(slot) > 1:
            raise DeviceNotUnique("disk - vm.py - find_disk()")
        for disk in self.disk_list:
            if disk.slot == slot:
                return disk

    def post_vm_payload(self, rest_client, ansible_dict):
        # The rest of the keys from VM_PAYLOAD_KEYS will get set properly automatically
        # Cloud init will be obtained through ansible_dict - If method will be reused outside of vm module,
        # cloud_init should be one of the ansible_dict's keys.
        payload = self.to_hypercore()
        VM._post_vm_payload_set_disks(payload, rest_client)
        payload["netDevs"] = [
            filter_dict(nic, *nic.keys()) for nic in payload["netDevs"]
        ]
        payload["bootDevices"] = []
        dom = filter_dict(payload, *VM_PAYLOAD_KEYS)
        cloud_init_payload = VM.create_cloud_init_payload(ansible_dict)
        if cloud_init_payload is not None:
            dom["cloudInitData"] = cloud_init_payload
        options = dict(attachGuestToolsISO=payload["attachGuestToolsISO"])
        return dict(dom=dom, options=options)

    @staticmethod
    def _post_vm_payload_set_disks(vm_hypercore_dict, rest_client):
        disks_payload = []
        primary_disk_set = False
        for disk in vm_hypercore_dict["blockDevs"]:
            disk_payload = dict(
                cacheMode=disk["cacheMode"] or "WRITETHROUGH",
                type=disk["type"],
                capacity=disk["capacity"] or 0,
            )
            if disk_payload["type"] == "IDE_CDROM" and disk["name"]:
                iso_name = disk["name"]
                iso = ISO.get_by_name(dict(name=iso_name), rest_client, must_exist=True)
                disk_payload["path"] = iso.path
            if not primary_disk_set and disk_payload["type"] != "IDE_CDROM":
                # Assign the first disk to be the primary
                # The first disk is assigned 'primaryDrive' property
                disk_payload["uuid"] = "primaryDrive"
                primary_disk_set = True
            disks_payload.append(disk_payload)
        vm_hypercore_dict["blockDevs"] = disks_payload

    def delete_unused_nics_to_hypercore_vm(self, module, rest_client, nic_key):
        changed = False
        ansible_nic_uuid_list = [
            nic["vlan_new"]
            if ("vlan_new" in nic.keys() and nic["vlan_new"])
            else nic["vlan"]
            for nic in module.params[nic_key] or []
        ]
        for nic in self.nic_list:
            if nic.vlan not in ansible_nic_uuid_list:
                self.do_shutdown_steps(module, rest_client)
                response = rest_client.delete_record(
                    endpoint="/rest/v1/VirDomainNetDevice/" + nic.uuid, check_mode=False
                )
                TaskTag.wait_task(rest_client, response)
                changed = True
        return changed, self.reboot

    def export_vm(self, rest_client, ansible_dict):
        data = VM.create_export_or_import_vm_payload(
            ansible_dict,
            None,
            is_export=True,
        )
        return rest_client.create_record(
            endpoint=f"/rest/v1/VirDomain/{self.uuid}/export",
            payload=data,
            check_mode=False,
            timeout=None,
        )

    def clone_vm(self, rest_client, ansible_dict):
        cloud_init_data = VM.create_cloud_init_payload(ansible_dict)
        data = VM.create_clone_vm_payload(
            ansible_dict["vm_name"], ansible_dict["tags"], self.tags, cloud_init_data
        )
        return rest_client.create_record(
            endpoint=f"/rest/v1/VirDomain/{self.uuid}/clone",
            payload=data,
            check_mode=False,
            timeout=None,
        )

    def __eq__(self, other):
        """One VM is equal to another if it has ALL attributes exactly the same"""
        return all(
            (
                self.operating_system == other.operating_system,
                self.uuid == other.uuid,
                self.node_uuid == other.node_uuid,
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
                self.node_affinity == other.node_affinity,
                self.snapshot_schedule == other.snapshot_schedule,
            )
        )

    def __str__(self):
        return super().__str__()

    def get_specific_nic(self, query):
        results = [nic.to_ansible() for nic in self.nics]
        return VM.filter_specific_objects(results, query, "Nic")

    def get_specific_disk(self, query):
        results = [vm_disk.to_ansible() for vm_disk in self.disks]
        return VM.filter_specific_objects(results, query, "Disk")

    @staticmethod
    def filter_specific_objects(results, query, object_type):
        # Type is type of the device, for example disk or nic
        filtered_results = filter_results(results, query)
        if len(filtered_results) > 1:
            raise ScaleComputingError(
                "{0} isn't uniquely identifyed by {1} in the VM.".format(
                    object_type, query
                )
            )
        return filtered_results[0] if filtered_results else None

    @staticmethod
    def get_vm_device_ansible_query(desired_vm_device_ansible):
        vm_device_raw_query = filter_dict(
            desired_vm_device_ansible, "disk_slot", "nic_vlan", "iso_name"
        )
        return transform_query(vm_device_raw_query, VM_DEVICE_QUERY_MAPPING_ANSIBLE)

    def get_vm_device(self, desired_vm_object):
        vm_device_query = VM.get_vm_device_ansible_query(desired_vm_object)
        if desired_vm_object["type"] == "nic":  # Retrieve Nic object
            return self.get_specific_nic(vm_device_query)
        vm_device_query["type"] = desired_vm_object["type"]
        return self.get_specific_disk(vm_device_query)  # Retrieve disk object

    def set_boot_devices_order(self, boot_items):
        boot_order = []
        for desired_boot_device in boot_items:
            vm_device = self.get_vm_device(desired_boot_device)
            if not vm_device:
                continue
            boot_order.append(vm_device["uuid"])
        return boot_order

    @staticmethod
    def update_boot_device_order(module, rest_client, vm, boot_order):
        # uuid is vm's uuid. boot_order is the desired order we want to set to boot devices
        vm.do_shutdown_steps(module, rest_client)
        task_tag = rest_client.update_record(
            "{0}/{1}".format("/rest/v1/VirDomain", vm.uuid),
            dict(bootDevices=boot_order),
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag)

    def set_boot_devices(
        self, boot_items, module, rest_client, previous_boot_order, changed=False
    ):
        desired_boot_order = self.set_boot_devices_order(boot_items)
        if desired_boot_order != previous_boot_order:
            VM.update_boot_device_order(module, rest_client, self, desired_boot_order)
            changed = True
        return changed

    @classmethod
    def get_vm_and_boot_devices(cls, ansible_dict, rest_client):
        """Helper to modules vm_boot_devices and vm."""
        vm = cls.get_by_name(ansible_dict, rest_client, must_exist=True)
        boot_devices_uuid = vm.get_boot_device_order()
        boot_devices_ansible = [
            boot_device.to_ansible() for boot_device in vm.boot_devices
        ]
        return vm, boot_devices_uuid, boot_devices_ansible

    def update_vm_power_state(self, module, rest_client, desired_power_state):
        """Sets the power state to what is stored in self.power_state"""
        # desired_power_state must be present in FROM_ANSIBLE_TO_HYPERCORE_ACTION_STATE's keys
        if not self.power_state:
            raise errors.ScaleComputingError("No information about VM's power state.")
        task_tag = rest_client.create_record(
            "/rest/v1/VirDomain/action",
            [
                dict(
                    virDomainUUID=self.uuid,
                    actionType=FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE[
                        desired_power_state
                    ],
                    cause="INTERNAL",
                )
            ],
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag)

    @classmethod
    def get_vm_device_list(cls, vm_hypercore_dict):
        all_vm_devices = vm_hypercore_dict["netDevs"] + vm_hypercore_dict["blockDevs"]
        vm_device_list = []
        for vm_device_uuid in vm_hypercore_dict["bootDevices"]:
            vm_device_hypercore = cls.filter_specific_objects(
                all_vm_devices, {"uuid": vm_device_uuid}, "Disk or nic"
            )
            if vm_device_hypercore["type"] in DISK_TYPES_HYPERCORE:
                vm_device_list.append(Disk.from_hypercore(vm_device_hypercore))
            else:  # The device is Nic
                vm_device_list.append(Nic.from_hypercore(vm_device_hypercore))
        return vm_device_list

    def get_boot_device_order(self):
        return [boot_device.uuid for boot_device in self.boot_devices]

    @staticmethod
    def called_from_vm_module(module_path):
        # if module_path == "scale_computing.hypercore.vm_disk":
        #     return True
        if module_path == "scale_computing.hypercore.vm":
            return True
        elif module_path in (
            "scale_computing.hypercore.vm_disk",
            "scale_computing.hypercore.vm_nic",
        ):
            return False
        raise ScaleComputingError(
            "Setting disks and/or is currently only supported in two of the following modules:"
            "scale_computing.hypercore.vm_disk, scale_computing.hypercore.vm, scale_computing.hypercore.vm_nic"
        )

    def vm_shutdown_forced(self, module, rest_client, reboot=False):
        # forces a VM power off, only if force_shutdown is true from ansbile.
        # Returns True if successful, False if unsuccessful
        if "force_reboot" not in module.params:
            raise errors.ScaleComputingError(
                "Force shutdown is not supported by this module."
            )
        # Get fresh VM data, in case vm_params changed power state.
        vm_fresh_data = rest_client.get_record(
            f"/rest/v1/VirDomain/{self.uuid}", must_exist=True
        )
        if vm_fresh_data["state"] in ["SHUTOFF", "SHUTDOWN"]:
            return True
        if (
            module.params["force_reboot"]
            and self.was_shutdown_tried
            and not self.reboot
        ):
            self.update_vm_power_state(module, rest_client, "stop")
            self.reboot = True
            return True
        return False

    def wait_shutdown(self, module, rest_client):
        # Sends a shutdown request and waits for VM to responde.
        # Send GET request every 10 seconds.
        # Returns True if successful, False if unsuccessful
        # Get fresh VM data, there is an error if VM is not running and shutdown request is sent.
        vm_fresh_data = rest_client.get_record(
            f"/rest/v1/VirDomain/{self.uuid}", must_exist=True
        )
        if vm_fresh_data["state"] in ["SHUTOFF", "SHUTDOWN"]:
            return True
        if (
            vm_fresh_data["state"] == "RUNNING"
            and module.params["shutdown_timeout"]
            and not self.was_shutdown_tried
        ):
            self.update_vm_power_state(module, rest_client, "shutdown")
            self.was_shutdown_tried = True
            shutdown_timeout = module.params["shutdown_timeout"]
            start = time()
            while 1:
                vm = rest_client.get_record(
                    f"/rest/v1/VirDomain/{self.uuid}", must_exist=True
                )
                current_time = time() - start
                if vm["state"] in ["SHUTDOWN", "SHUTOFF"]:
                    self.reboot = True
                    return True
                if current_time >= shutdown_timeout:
                    return False
                sleep(10)
        return False

    def vm_power_up(self, module, rest_client):
        # Powers up a VM in case it was shutdown during module action.
        if self.reboot:
            self.update_vm_power_state(module, rest_client, "start")

    def do_shutdown_steps(self, module, rest_client):
        if not self.wait_shutdown(module, rest_client):
            if not self.vm_shutdown_forced(module, rest_client):
                raise errors.ScaleComputingError(
                    f"VM - {self.name} - needs to be powered off and is not responding to a shutdown request."
                )


class ManageVMParams(VM):
    @staticmethod
    def _build_payload(module, rest_client):
        payload = {}
        if module.params["vm_name_new"]:
            payload["name"] = module.params["vm_name_new"]
        if module.params["description"] is not None:  # we want to be able to write ""
            payload["description"] = module.params["description"]
        if module.params["tags"] is not None:  # we want to be able to write ""
            payload["tags"] = ",".join(
                module.params["tags"]
            )  # tags is a list of strings
        if module.params["memory"]:
            payload["mem"] = module.params["memory"]
        if module.params["vcpu"] is not None:
            payload["numVCPU"] = module.params["vcpu"]
        if (
            module.params["snapshot_schedule"] is not None
        ):  # we want to be able to write ""
            if module.params["snapshot_schedule"] == "":
                payload["snapshotScheduleUUID"] = ""
            else:
                query = {"name": module.params["snapshot_schedule"]}
                snapshot_schedule = SnapshotSchedule.get_snapshot_schedule(
                    query, rest_client, must_exist=True
                )
                payload["snapshotScheduleUUID"] = snapshot_schedule.uuid
        return payload

    @staticmethod
    def _needs_reboot(module, changed):
        for param in module.params:
            if (
                module.params[param] is not None and param in REBOOT_LOOKUP
            ):  # skip not provided parameters and cluster_instance
                if REBOOT_LOOKUP[param] and changed[param]:
                    return True
        return False

    @staticmethod
    def _to_be_changed(vm, module):
        changed_params = {}
        if module.params["vm_name_new"]:
            changed_params["vm_name"] = vm.name != module.params["vm_name_new"]
        if module.params["description"] is not None:  # we want to be able to write ""
            changed_params["description"] = (
                vm.description != module.params["description"]
            )
        if module.params["tags"] is not None:  # we want to be able to write ""
            changed_params["tags"] = vm.tags != module.params["tags"]
        if module.params["memory"]:
            changed_params["memory"] = vm.mem != module.params["memory"]
        if module.params["vcpu"] is not None:
            changed_params["vcpu"] = vm.numVCPU != module.params["vcpu"]
        if module.params["power_state"]:
            # This is comparison between two strings. This works because module.params["power_state"]
            # is in FROM_ANSIBLE_TO_HYPERCORE_POWER_STATE.keys(), whereas vm.power_state
            # is in FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE.values().
            # state in playbook is different than read from HC3 (start/started)
            is_substring = module.params["power_state"] not in vm.power_state
            changed_params["power_state"] = is_substring
        if (
            module.params["snapshot_schedule"] is not None
        ):  # we want to be able to write ""
            changed_params["snapshot_schedule"] = (
                vm.snapshot_schedule != module.params["snapshot_schedule"]
            )
        return any(changed_params.values()), changed_params

    @staticmethod
    def _build_after_diff(module, rest_client):
        after = {}
        if module.check_mode:
            if module.params["vm_name_new"]:
                after["vm_name"] = module.params["vm_name_new"]
            if module.params["description"] is not None:
                after["description"] = module.params["description"]
            if module.params["tags"] is not None:
                after["tags"] = module.params["tags"]
            if module.params["memory"]:
                after["memory"] = module.params["memory"]
            if module.params["vcpu"]:
                after["vcpu"] = module.params["vcpu"]
            if module.params["power_state"]:
                after["power_state"] = module.params["power_state"]
            if module.params["snapshot_schedule"] is not None:
                after["snapshot_schedule"] = module.params["snapshot_schedule"]
            return after
        query = {
            "name": module.params["vm_name_new"]
            if module.params["vm_name_new"]
            else module.params["vm_name"]
        }
        vm = VM.get_or_fail(query, rest_client)[0]
        if module.params["vm_name_new"]:
            after["vm_name"] = vm.name
        if module.params["description"] is not None:
            after["description"] = vm.description
        if module.params["tags"] is not None:
            after["tags"] = vm.tags
        if module.params["memory"]:
            after["memory"] = vm.mem
        if module.params["vcpu"]:
            after["vcpu"] = vm.numVCPU
        if module.params["power_state"]:
            after["power_state"] = vm.power_state
        if module.params["snapshot_schedule"] is not None:
            after["snapshot_schedule"] = vm.snapshot_schedule
        return after

    @staticmethod
    def _build_before_diff(vm, module):
        before = {}
        if module.params["vm_name_new"]:
            before["vm_name"] = vm.name
        if module.params["description"] is not None:
            before["description"] = vm.description
        if module.params["tags"] is not None:
            before["tags"] = vm.tags
        if module.params["memory"]:
            before["memory"] = vm.mem
        if module.params["vcpu"]:
            before["vcpu"] = vm.numVCPU
        if module.params["power_state"]:
            before["power_state"] = vm.power_state
        if module.params["snapshot_schedule"] is not None:
            before["snapshot_schedule"] = vm.snapshot_schedule
        return before

    @staticmethod
    def set_vm_params(module, rest_client, vm):
        changed, changed_parameters = ManageVMParams._to_be_changed(vm, module)
        if changed:
            payload = ManageVMParams._build_payload(module, rest_client)
            endpoint = "{0}/{1}".format("/rest/v1/VirDomain", vm.uuid)
            task_tag = rest_client.update_record(endpoint, payload, module.check_mode)
            TaskTag.wait_task(rest_client, task_tag)
            if ManageVMParams._needs_reboot(
                module, changed_parameters
            ) and vm.power_state not in ["stop", "stopped", "shutdown"]:
                vm.do_shutdown_steps(module, rest_client)
            else:
                # power_state needs different endpoint
                # Wait_task in update_vm_power_state doesn't handle check_mode
                if module.params["power_state"] and not module.check_mode:
                    vm.update_vm_power_state(
                        module, rest_client, module.params["power_state"]
                    )
            return (
                True,
                vm.reboot,
                dict(
                    before=ManageVMParams._build_before_diff(vm, module),
                    after=ManageVMParams._build_after_diff(module, rest_client),
                ),
            )
        else:
            return (
                False,
                False,
                dict(before=None, after=None),
            )


class ManageVMDisks:
    @staticmethod
    def get_vm_by_name(module, rest_client):
        """
        Wrapps VM's method get_by_name. Additionally, it raises exception if vm isn't found
        Returns vm object and list of ansible disks (this combo is commonly used in this module).
        """
        # If there's no VM with such name, error is raised automatically
        vm = VM.get_by_name(module.params, rest_client, must_exist=True)
        return vm, [disk.to_ansible() for disk in vm.disks]

    @staticmethod
    def _create_block_device(module, rest_client, vm, desired_disk):
        # vm is instance of VM, desired_disk is instance of Disk
        payload = desired_disk.post_and_patch_payload(vm)
        task_tag = rest_client.create_record(
            "/rest/v1/VirDomainBlockDevice",
            payload,
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag, module.check_mode)
        return task_tag["createdUUID"]

    @staticmethod
    def iso_image_management(module, rest_client, iso, uuid, attach):
        # iso is instance of ISO, uuid is uuid of block device
        # Attach is boolean. If true, you're attaching an image.
        # If false, it means you're detaching an image.
        payload = iso.attach_iso_payload() if attach else iso.detach_iso_payload()
        task_tag = rest_client.update_record(
            "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", uuid),
            payload,
            module.check_mode,
        )
        # Not returning anything, since it isn't used in code.
        # Disk's uuid is stored in task_tag if relevant in the future.
        TaskTag.wait_task(rest_client, task_tag, module.check_mode)

    @staticmethod
    def _update_block_device(module, rest_client, desired_disk, existing_disk, vm):
        payload = desired_disk.post_and_patch_payload(vm)
        if existing_disk.needs_reboot(desired_disk):
            vm.do_shutdown_steps(module, rest_client)
        task_tag = rest_client.update_record(
            "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", existing_disk.uuid),
            payload,
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag, module.check_mode)
        return vm.reboot

    @classmethod
    def _delete_not_used_disks(cls, module, rest_client, vm, changed, disk_key):
        updated_vm, updated_ansible_disks = cls.get_vm_by_name(module, rest_client)
        # Ensure all disk that aren't listed in items don't exist in VM (ensure absent)
        for updated_ansible_disk in updated_ansible_disks:
            existing_disk = Disk.from_ansible(updated_ansible_disk)
            to_delete = True
            for ansible_desired_disk in module.params[disk_key]:
                desired_disk = Disk.from_ansible(ansible_desired_disk)
                if (
                    desired_disk.slot == existing_disk.slot
                    and desired_disk.type == existing_disk.type
                ):
                    to_delete = False
            if to_delete:
                # VM needs to be stopped before delete action
                vm.do_shutdown_steps(module, rest_client)
                task_tag = rest_client.delete_record(
                    "{0}/{1}".format(
                        "/rest/v1/VirDomainBlockDevice", existing_disk.uuid
                    ),
                    module.check_mode,
                )
                TaskTag.wait_task(rest_client, task_tag, module.check_mode)
                changed = True
        return changed

    @staticmethod
    def _force_remove_all_disks(module, rest_client, vm, disks_before):
        # It's important to check if items is equal to empty list and empty list only (no None-s)
        # This method is going to be called in vm_disk class only.
        if module.params["items"] != []:
            raise ScaleComputingError(
                "If force set to true, items should be set to empty list"
            )
        # Delete all disks
        for existing_disk in vm.disks:
            vm.do_shutdown_steps(module, rest_client)
            task_tag = rest_client.delete_record(
                "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", existing_disk.uuid),
                module.check_mode,
            )
            TaskTag.wait_task(rest_client, task_tag, module.check_mode)
        return True, [], dict(before=disks_before, after=[]), vm.reboot

    @classmethod
    def ensure_present_or_set(cls, module, rest_client, module_path):
        # At the moment, this method is called in modules vm_disk and vm
        # Module path is here to distinguish from which module ensure_present_or_set was called from
        changed = False
        called_from_vm_disk = not VM.called_from_vm_module(module_path)
        disk_key = "items" if called_from_vm_disk else "disks"
        vm_before, disks_before = cls.get_vm_by_name(module, rest_client)
        if (
            called_from_vm_disk
            and module.params["state"] == "set"
            and module.params["force"]
        ):
            return cls._force_remove_all_disks(
                module, rest_client, vm_before, disks_before
            )
        for ansible_desired_disk in module.params[disk_key]:
            # For the given VM, disk can be uniquely identified with disk_slot and type or
            # just name, if not empty string
            disk_query = filter_dict(ansible_desired_disk, "disk_slot", "type")
            ansible_existing_disk = vm_before.get_specific_disk(disk_query)
            desired_disk = Disk.from_ansible(ansible_desired_disk)
            if ansible_desired_disk["type"] == "ide_cdrom":
                if ansible_existing_disk:
                    if (
                        ansible_existing_disk["iso_name"]
                        == ansible_desired_disk["iso_name"]
                    ):
                        continue  # CD-ROM with such iso_name already exists
                    existing_disk = Disk.from_ansible(ansible_existing_disk)
                    uuid = existing_disk.uuid
                else:
                    # Create new ide_cdrom disk
                    # size is not relevant when creating CD-ROM -->
                    # https://github.com/ScaleComputing/HyperCoreAnsibleCollection/issues/11
                    desired_disk.size = 0
                    uuid = cls._create_block_device(
                        module, rest_client, vm_before, desired_disk
                    )
                    changed = True
                # Attach ISO image
                # If ISO image's name is specified, it's assumed you want to attach ISO image
                name = ansible_desired_disk["iso_name"]
                if name:  # Not creating empty CD-ROM without attaching anything
                    iso = ISO.get_by_name(dict(name=name), rest_client, must_exist=True)
                    cls.iso_image_management(
                        module, rest_client, iso, uuid, attach=True
                    )
                    changed = True
            else:
                if ansible_existing_disk:
                    existing_disk = Disk.from_ansible(ansible_existing_disk)
                    # Check superset for idempotency
                    ansible_desired_disk_filtered = {
                        k: v
                        for k, v in desired_disk.to_ansible().items()
                        if v is not None
                    }
                    if is_superset(
                        ansible_existing_disk, ansible_desired_disk_filtered
                    ):
                        # There's nothing to do - all properties are already set the way we want them to be
                        continue

                    cls._update_block_device(
                        module, rest_client, desired_disk, existing_disk, vm_before
                    )
                else:
                    cls._create_block_device(
                        module, rest_client, vm_before, desired_disk
                    )
                changed = True
        if module.params["state"] == "set" or not called_from_vm_disk:
            changed = cls._delete_not_used_disks(
                module, rest_client, vm_before, changed, disk_key
            )
        if called_from_vm_disk:
            vm_after, disks_after = cls.get_vm_by_name(module, rest_client)
            return (
                changed,
                disks_after,
                dict(before=disks_before, after=disks_after),
                vm_before.reboot,
            )
        return changed, vm_before.reboot


class ManageVMNics(Nic):
    @classmethod
    def get_by_uuid(cls, rest_client, nic_uuid):
        return Nic.from_hypercore(
            rest_client.get_record(
                "/rest/v1/VirDomainNetDevice", query={"uuid": nic_uuid}, must_exist=True
            )
        )

    @classmethod
    def send_update_nic_request_to_hypercore(
        cls,
        module,
        virtual_machine_obj,
        rest_client,
        new_nic,
        existing_nic,
        before,
        after,
    ):
        if new_nic is None or existing_nic is None:
            raise errors.MissingFunctionParameter(
                "new_nic or existing_nic - nic.py - update_nic_to_hypercore()"
            )
        before.append(existing_nic.to_ansible())
        data = new_nic.to_hypercore()
        virtual_machine_obj.do_shutdown_steps(module, rest_client)
        response = rest_client.update_record(
            endpoint="/rest/v1/VirDomainNetDevice/" + existing_nic.uuid,
            payload=data,
            check_mode=False,
        )
        new_nic_obj = ManageVMNics.get_by_uuid(
            rest_client=rest_client, nic_uuid=existing_nic.uuid
        )
        after.append(new_nic_obj.to_ansible())
        TaskTag.wait_task(rest_client=rest_client, task=response)
        return True, before, after, virtual_machine_obj.reboot

    @classmethod
    def send_create_nic_request_to_hypercore(
        cls, module, virtual_machine_obj, rest_client, new_nic, before, after
    ):
        if new_nic is None:
            raise errors.MissingFunctionParameter(
                "new_nic - nic.py - create_nic_to_hypercore()"
            )
        before.append(None)
        data = new_nic.to_hypercore()
        virtual_machine_obj.do_shutdown_steps(module, rest_client)
        response = rest_client.create_record(
            endpoint="/rest/v1/VirDomainNetDevice", payload=data, check_mode=False
        )
        new_nic_obj = ManageVMNics.get_by_uuid(
            rest_client=rest_client, nic_uuid=response["createdUUID"]
        )
        after.append(new_nic_obj.to_ansible())
        TaskTag.wait_task(rest_client=rest_client, task=response)
        return True, before, after, virtual_machine_obj.reboot

    @classmethod
    def send_delete_nic_request_to_hypercore(
        cls, virtual_machine_obj, module, rest_client, nic_to_delete, before, after
    ):
        if nic_to_delete is None:
            raise errors.MissingFunctionParameter(
                "nic_to_delete - nic.py - delete_nic_to_hypercore()"
            )
        before.append(nic_to_delete.to_ansible())
        virtual_machine_obj.do_shutdown_steps(module, rest_client)
        response = rest_client.delete_record(
            endpoint="/rest/v1/VirDomainNetDevice/" + nic_to_delete.uuid,
            check_mode=False,
        )
        after.append(None)
        TaskTag.wait_task(rest_client=rest_client, task=response)
        return True, before, after, virtual_machine_obj.reboot

    @classmethod
    def ensure_present_or_set(cls, module, rest_client, module_path):
        before = []
        after = []
        changed = False
        called_from_vm_nic = not VM.called_from_vm_module(module_path)
        nic_key = "items" if called_from_vm_nic else "nics"
        virtual_machine_obj_list = VM.get_or_fail(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )
        if module.params[nic_key]:
            for nic in module.params[nic_key]:
                nic["vm_uuid"] = virtual_machine_obj_list[0].uuid
                nic = Nic.from_ansible(ansible_data=nic)
                existing_hc3_nic, existing_hc3_nic_with_new = virtual_machine_obj_list[
                    0
                ].find_nic(
                    vlan=nic.vlan,
                    mac=nic.mac,
                    vlan_new=nic.vlan_new,
                    mac_new=nic.mac_new,
                )
                if existing_hc3_nic_with_new and Nic.is_update_needed(
                    existing_hc3_nic_with_new, nic
                ):  # Update existing with vlan_new or mac_new - corner case
                    (
                        changed,
                        before,
                        after,
                        reboot,
                    ) = ManageVMNics.send_update_nic_request_to_hypercore(
                        module,
                        virtual_machine_obj_list[0],
                        rest_client,
                        nic,
                        existing_hc3_nic_with_new,
                        before,
                        after,
                    )
                elif (
                    existing_hc3_nic  # Nic
                    and not existing_hc3_nic_with_new  # None
                    and Nic.is_update_needed(existing_hc3_nic, nic)  # True
                ):  # Update existing
                    (
                        changed,
                        before,
                        after,
                        reboot,
                    ) = ManageVMNics.send_update_nic_request_to_hypercore(
                        module,
                        virtual_machine_obj_list[0],
                        rest_client,
                        nic,
                        existing_hc3_nic,
                        before,
                        after,
                    )
                # Create new
                elif not existing_hc3_nic and not existing_hc3_nic_with_new:
                    (
                        changed,
                        before,
                        after,
                        reboot,
                    ) = ManageVMNics.send_create_nic_request_to_hypercore(
                        module,
                        virtual_machine_obj_list[0],
                        rest_client=rest_client,
                        new_nic=nic,
                        before=before,
                        after=after,
                    )
        elif module.params[nic_key] == []:  # empty set in ansible, delete all
            for nic in virtual_machine_obj_list[0].nic_list:
                before.append(nic.to_ansible())
        else:
            raise errors.MissingValueAnsible(
                "items, cannot be null, empty must be set to []"
            )
        updated_virtual_machine = VM.get(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )[0]
        if module.params["state"] == NicState.set or not called_from_vm_nic:
            # Check if any nics need to be deleted from the vm
            if updated_virtual_machine.delete_unused_nics_to_hypercore_vm(
                module, rest_client, nic_key
            )[0]:
                changed = True
                virtual_machine_obj_list[0].reboot = True
        if called_from_vm_nic:
            return (
                changed,
                after,
                dict(before=before, after=after),
                virtual_machine_obj_list[0].reboot,
            )
        return changed, virtual_machine_obj_list[0].reboot
