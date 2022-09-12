# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import base64

from ..module_utils.errors import DeviceNotUnique
from ..module_utils.nic import Nic
from ..module_utils.disk import Disk
from ..module_utils.node import Node
from ..module_utils.iso import ISO
from ..module_utils.utils import PayloadMapper, filter_dict, transform_query
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
    pause="PAUSE",
    rebot="REBOOT",
    reset="RESET",
    livemigrate="LIVEMIGRATE",
    started="START",
)

DEFAULT_DISK_CDROM_PAYLOAD = dict(
    cacheMode="WRITETHROUGH",
    path="",
    type="IDE_CDROM",
    uuid="cdrom",
    capacity=0,
)

DEFAULT_DISK_OTHER_PAYLOAD = dict(
    cacheMode="WRITETHROUGH",
    path="",
    uuid="primaryDrive",
)

DEFAULT_MACHINE_TYPE = "scale-7.2"
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
            snapshot_schedule=snapshot_schedule.name if snapshot_schedule else None,
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
            pathURI = f"smb://{ansible_dict['smb']['username']}:{ansible_dict['smb']['password']}@{ansible_dict['smb']['server']}/{ansible_dict['smb']['path']}"
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
    def get_by_name(cls, ansible_dict, rest_client, must_exist=False):
        """
        With given dict from playbook, finds the existing vm by name from the HyperCore api and constructs object VM if
        the record exists. If there is no record with such name, None is returned.
        """
        query = get_query(
            ansible_dict, "vm_name", ansible_hypercore_map=dict(vm_name="name")
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
        # TODO we need to find by (name, disk_type, disk_slot).
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
        payload["machineType"] = DEFAULT_MACHINE_TYPE
        payload["netDevs"] = [
            filter_dict(nic, *nic.keys()) for nic in payload["netDevs"]
        ]
        payload["bootDevices"] = []
        dom = filter_dict(payload, *VM_PAYLOAD_KEYS)
        cloud_init_payload = VM.create_cloud_init_payload(ansible_dict)
        if cloud_init_payload is not None:
            dom["CloudIinitData"] = cloud_init_payload
        options = dict(attachGuestToolsISO=payload["attachGuestToolsISO"])
        return dict(dom=dom, options=options)

    @staticmethod
    def _post_vm_payload_set_disks(vm_hypercore_dict, rest_client):
        disks_payload = []
        cdrom_exists = False
        primary_disk_set = False
        for disk in vm_hypercore_dict["blockDevs"]:
            disk_payload = dict()
            if disk.get("cacheMode", None):
                disk_payload["cacheMode"] = disk["cacheMode"]
            else:
                disk_payload["cacheMode"] = DEFAULT_DISK_CDROM_PAYLOAD["cacheMode"]
            disk_payload["type"] = disk["type"]
            disk_payload["capacity"] = disk["capacity"] or 0
            if disk_payload["type"] == "IDE_CDROM":
                iso_name = disk["name"]
                iso = ISO.get_by_name(dict(name=iso_name), rest_client, must_exist=True)
                disk_payload["path"] = iso.path
                cdrom_exists = True
            if not primary_disk_set and disk_payload["type"] != "IDE_CDROM":
                # Assign the first disk to be the primary
                disk_payload["uuid"] = DEFAULT_DISK_OTHER_PAYLOAD["uuid"]
                primary_disk_set = True
            disks_payload.append(disk_payload)
        if not cdrom_exists:
            disks_payload.insert(0, DEFAULT_DISK_CDROM_PAYLOAD)
        vm_hypercore_dict["blockDevs"] = disks_payload

    def delete_unused_nics_to_hypercore_vm(self, ansible_dict, rest_client):
        changed = False
        ansible_nic_uuid_list = [
            nic["vlan_new"]
            if ("vlan_new" in nic.keys() and nic["vlan_new"])
            else nic["vlan"]
            for nic in ansible_dict["items"] or []
        ]
        for nic in self.nic_list:
            if nic.vlan not in ansible_nic_uuid_list:
                response = rest_client.delete_record(
                    endpoint="/rest/v1/VirDomainNetDevice/" + nic.uuid, check_mode=False
                )
                TaskTag.wait_task(rest_client, response)
                changed = True
        return changed

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
    def update_boot_device_order(module, rest_client, uuid, boot_order):
        # uuid is vm's uuid. boot_order is the desired order we want to set to boot devices
        task_tag = rest_client.update_record(
            "{0}/{1}".format("/rest/v1/VirDomain", uuid),
            dict(bootDevices=boot_order, uuid=uuid),
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag)

    def set_boot_devices(
        self, boot_items, module, rest_client, previous_boot_order, changed=False
    ):
        desired_boot_order = self.set_boot_devices_order(boot_items)
        if desired_boot_order != previous_boot_order:
            VM.update_boot_device_order(
                module, rest_client, self.uuid, desired_boot_order
            )
            changed = True
        return changed

    @classmethod
    def get_vm_and_boot_devices(cls, ansible_dict, rest_client):
        """Helper to modules vm_boot_devices and vm."""
        vm = cls.get_by_name(ansible_dict, rest_client, must_exist=True)
        boot_devices_uuid = [boot_device.uuid for boot_device in vm.boot_devices]
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
