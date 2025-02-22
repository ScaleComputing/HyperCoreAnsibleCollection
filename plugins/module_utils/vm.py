# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

import base64
from time import sleep, time
from typing import Dict, Any, Optional, List

from ..module_utils.errors import DeviceNotUnique
from ..module_utils.rest_client import RestClient
from ..module_utils.nic import Nic, NicType
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
from ..module_utils.snapshot_schedule import SnapshotSchedule
from ..module_utils.hypercore_version import HyperCoreVersion

# HyperCore state (ansible power_state) are a state machine.
# We have states and actions to move between states.
FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE = dict(
    RUNNING="started",
    SHUTOFF="stopped",
    BLOCKED="blocked",
    PAUSED="paused",
    SHUTDOWN="shutdown",
    CRASHED="crashed",
)

FROM_ANSIBLE_TO_HYPERCORE_POWER_ACTION = dict(
    start="START",
    shutdown="SHUTDOWN",
    stop="STOP",
    reboot="REBOOT",
    reset="RESET",
    started="START",  # TODO remove?
)

FROM_ANSIBLE_POWER_ACTION_TO_ANSIBLE_POWER_STATE = dict(
    start="started",
    # both "stop" and "shutdown" result in "stopped" state
    shutdown="stopped",
    stop="stopped",
    reboot="started",
    reset="started",
    started="started",  # TODO remove?
)

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
    "operatingSystem",
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

# List VM params that require VM reboot,
# either because VM then can be changed only if VM is shutdown,
# or because change is applied only after shutdown.
REBOOT_LOOKUP = dict(
    vm_name=False,
    description=False,
    tags=False,
    memory=True,
    vcpu=True,
    power_state=False,
    snapshot_schedule=False,
    machine_type=True,
)


class VmMachineType:
    # In table below is left side output from 'sc vmmachinetypes show' command,
    # on most recent HyperCore version.
    _map_hypercore_to_ansible = {
        "scale-bios-9.3": "BIOS",
        "scale-7.2": "BIOS",  # ?
        "scale-5.4": "BIOS",  # ?
        "scale-8.10": "UEFI",
        "scale-uefi-9.3": "UEFI",
        "scale-uefi-tpm-compatible-9.3": "vTPM+UEFI-compatible",
        "scale-bios-lsi-9.2": "BIOS",  # ?
        "scale-uefi-tpm-9.3": "vTPM+UEFI",
        "scale-6.4": "BIOS",  # ?
        "scale-uefi-tpm-9.2": "vTPM+UEFI",
    }

    # Check in GUI what exactly is sent for selected VM machine type
    # when creating a new VM.
    # On 9.1.14.208456
    _map_ansible_to_hypercore_91 = {
        "BIOS": "scale-7.2",
        "UEFI": "scale-8.10",
    }
    # On 9.2.13.211102
    _map_ansible_to_hypercore_92 = {
        "BIOS": "scale-7.2",
        "UEFI": "scale-8.10",
        "vTPM+UEFI": "scale-uefi-tpm-9.2",
    }
    # On 9.3.1.212486 (pre-release)
    _map_ansible_to_hypercore_93 = {
        "BIOS": "scale-bios-9.3",
        "UEFI": "scale-uefi-9.3",
        "vTPM+UEFI": "scale-uefi-tpm-9.3",
        "vTPM+UEFI-compatible": "scale-uefi-tpm-compatible-9.3",
    }
    # HyperCore machineTypeKeyword can be: "bios" "uefi" "tpm" "tpm-compatible"
    _map_ansible_to_hypercore_machine_type_keyword = {
        "BIOS": "bios",
        "UEFI": "uefi",
        "vTPM+UEFI": "tpm",
        "vTPM+UEFI-compatible": "tpm-compatible",
    }

    @classmethod
    def from_ansible_to_hypercore(
        cls, ansible_machine_type: str, hcversion: HyperCoreVersion
    ) -> str:
        # Empty string is returned if ansible_machine_type cannot bve used with give HyperCore version.
        if not ansible_machine_type:
            return ""
        if hcversion.verify(">=9.3.0"):
            map_ansible_to_hypercore = cls._map_ansible_to_hypercore_93
        elif hcversion.verify(">=9.2.0"):
            map_ansible_to_hypercore = cls._map_ansible_to_hypercore_92
        else:
            # hcversion >=9.1.0, might work with earlier version too
            map_ansible_to_hypercore = cls._map_ansible_to_hypercore_91
        return map_ansible_to_hypercore.get(ansible_machine_type, "")

    @classmethod
    def from_hypercore_to_ansible(cls, vm_dict: dict) -> str:
        # We receive whole vm_dict as returned by HC3,
        # and use machineTypeKeyword if present.
        if "machineTypeKeyword" in vm_dict:
            _map_hypercore_machine_type_keyword_to_ansible = {
                cls._map_ansible_to_hypercore_machine_type_keyword[k]: k
                for k in cls._map_ansible_to_hypercore_machine_type_keyword
            }
            # "machineTypeKeyword" is available in HyperCore 9.3 or later
            return _map_hypercore_machine_type_keyword_to_ansible.get(
                vm_dict["machineTypeKeyword"], ""
            )
        return cls._map_hypercore_to_ansible.get(vm_dict["machineType"], "")

    @classmethod
    def from_ansible_to_hypercore_machine_type_keyword(cls, ansible_machine_type: str):
        return cls._map_ansible_to_hypercore_machine_type_keyword[ansible_machine_type]


def compute_params_disk_slot(module, disk_key: str):
    # Some params can be computed or ignored.
    # For NVRAM and VTPM disks the disk slot is ignored.
    # API will always return disk_slot=-1.
    # Ignore different user provided values.
    # disk_key is "disks" for vm module, "items" for vm_disk module.
    disks = module.params.get(disk_key, [])
    # disks might be None.
    disks = disks or []
    for disk in disks:
        if disk["type"] in ["nvram", "vtpm"]:
            if "disk_slot" in disk and disk["disk_slot"] != -1:
                module.warn(
                    f"Disk with type={disk['type']} can have only disk_slot -1; ignoring provided value {disk['disk_slot']}."
                )
                disk["disk_slot"] = -1


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
        power_action=None,
        nics=None,  # nics represents a list of type Nic
        disks=None,  # disks represents a list of type Nic
        # boot_devices are stored as list of nics and/or disks internally.
        boot_devices=None,
        attach_guest_tools_iso=False,
        operating_system=None,
        node_affinity=None,
        snapshot_schedule=None,
        # _was_nice_shutdown_tried=False,  # Has shutdown request already been tried
        machine_type=None,
        replication_source_vm_uuid=None,
        snapshot_uuids=None,
    ):
        self.operating_system = operating_system
        self.uuid = uuid
        self.node_uuid = node_uuid
        self.name = name
        self.tags = tags
        self.description = description
        self.mem = memory
        self.numVCPU = vcpu
        self.nics = nics or []
        self.disks = disks or []
        self.boot_devices = boot_devices or []
        self.attach_guest_tools_iso = attach_guest_tools_iso
        self.node_affinity = node_affinity
        self.snapshot_schedule = snapshot_schedule  # name of the snapshot_schedule
        self.snapshot_uuids = snapshot_uuids or []
        self.machine_type = machine_type
        self.replication_source_vm_uuid = replication_source_vm_uuid

        power_state_values = list(FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE.values()) + [
            None
        ]
        power_action_values = list(FROM_ANSIBLE_TO_HYPERCORE_POWER_ACTION.keys()) + [
            None
        ]
        if power_state not in power_state_values:
            raise AssertionError(f"Unknown VM power_state={power_state}")
        if power_action not in power_action_values:
            raise AssertionError(f"Unknown VM power_action={power_action}")
        # VM.from_hypercore() will get only power_state
        # VM.from_ansible() will get only power_action
        if power_state and power_action:
            # is bug, or is this useful?
            raise AssertionError(
                f"Both power_state={power_state} and power_action={power_action} are set"
            )
        if power_state is None and power_action is None:
            # is bug, or is this useful?
            raise AssertionError(
                f"Neither power_state={power_state} nor power_action={power_action} is set"
            )
        self._power_state = power_state
        self._power_action = power_action
        if power_state and power_action is None:
            # compute required action (if current state is known)
            pass
        if power_state is None and power_action:
            # compute final power_state after action is applied
            pass
            # self._power_state = FROM_ANSIBLE_POWER_ACTION_TO_ANSIBLE_POWER_STATE[power_action]

        self._initially_running = power_state == "started"
        # .was_nice_shutdown_tried is True if nice ACPI shutdown was tried
        self._was_nice_shutdown_tried = False
        # if nice shutdown was tried, did it work?
        self._did_nice_shutdown_work = False
        # ._was_force_shutdown_tried is True if force shutdown (stop) was tried
        self._was_force_shutdown_tried = False
        # self._did_force_shutdown_work = False
        self._was_start_tried = False
        # self._did_start_work = False
        # Now, VM was rebooted when it was running at start, then stopped and powered on:
        # .power_state in [] and any(_did_nice_shutdown_work, _did_force_shutdown_work) and _was_start_tried
        self._was_reboot_tried = False
        self._was_reset_tried = False

    @property
    def nic_list(self):
        return self.nics

    @property
    def disk_list(self):
        return self.disks

    @classmethod
    def from_ansible(cls, ansible_data):
        vm_dict = ansible_data

        # Unfortunately we were using in playbooks "start" instead of "started", etc.
        # Ansible module param with name "power_state" is actually power_action.
        power_action = vm_dict.get("power_state", None)

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
            operating_system=vm_dict.get("operating_system"),
            power_action=power_action,
            machine_type=vm_dict.get("machine_type", None),
        )

    @classmethod
    def from_hypercore(cls, vm_dict, rest_client) -> Optional[VM]:
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
            preferred_node=(
                preferred_node.to_ansible()
                if preferred_node
                else dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                )
            ),  # for vm_node_affinity diff check
            backup_node=(
                backup_node.to_ansible()
                if backup_node
                else dict(
                    node_uuid="",
                    backplane_ip="",
                    lan_ip="",
                    peer_id=None,
                )
            ),  # for vm_node_affinity diff check,
        )

        snapshot_schedule = SnapshotSchedule.get_snapshot_schedule(
            query={"uuid": vm_dict["snapshotScheduleUUID"]}, rest_client=rest_client
        )
        machine_type = VmMachineType.from_hypercore_to_ansible(vm_dict)
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
            snapshot_schedule=(
                snapshot_schedule.name if snapshot_schedule else ""
            ),  # "" for vm_params diff check
            snapshot_uuids=vm_dict["snapUUIDs"],
            machine_type=machine_type,
            replication_source_vm_uuid=vm_dict["sourceVirDomainUUID"],
        )

    @classmethod
    def create_cloud_init_payload(cls, ansible_dict):
        if "cloud_init" in ansible_dict.keys() and (
            ansible_dict["cloud_init"]["user_data"]
            or ansible_dict["cloud_init"]["meta_data"]
        ):
            return dict(
                userData=(
                    str(
                        base64.b64encode(
                            bytes(str(ansible_dict["cloud_init"]["user_data"]), "utf-8")
                        )
                    )[2:-1]
                    if ansible_dict["cloud_init"]["user_data"] is not None
                    else ""
                ),
                metaData=(
                    str(
                        base64.b64encode(
                            bytes(str(ansible_dict["cloud_init"]["meta_data"]), "utf-8")
                        )
                    )[2:-1]
                    if ansible_dict["cloud_init"]["meta_data"] is not None
                    else ""
                ),
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
        cls,
        clone_name,
        ansible_tags,
        hypercore_tags,
        cloud_init,
        *,
        preserve_mac_address,
        source_nics,
        source_snapshot_uuid,
    ):
        data = dict(template=dict())
        if source_snapshot_uuid:
            data["snapUUID"] = source_snapshot_uuid
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
        if preserve_mac_address:
            data["template"]["netDevs"] = [
                dict(
                    type=NicType.ansible_to_hypercore(nic.type),
                    macAddress=nic.mac,
                    vlan=nic.vlan,
                )
                for nic in source_nics
            ]
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
        cls,
        ansible_dict: Dict[Any, Any],
        rest_client: RestClient,
        must_exist: bool = False,
        name_field: str = "vm_name",
    ) -> Optional[VM]:
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
    def get_by_old_or_new_name(cls, ansible_dict, rest_client, must_exist=False):
        vm_old_name = VM.get_by_name(ansible_dict, rest_client)
        vm_new_name = (
            VM.get_by_name(ansible_dict, rest_client, name_field="vm_name_new")
            if ansible_dict.get("vm_name_new") is not None
            else None
        )
        if vm_old_name and vm_new_name:
            # Having two candidate VMs is error, we cannot decide which VM to modify.
            raise errors.ScaleComputingError(
                f"More than one VM matches requirement vm_name=={ansible_dict['vm_name']} or vm_name_new=={ansible_dict['vm_name_new']}"
            )
        vm = vm_old_name or vm_new_name
        if must_exist and vm is None:
            raise errors.VMNotFound(
                f"vm_name={ansible_dict['vm_name']} or vm_name_new={ansible_dict['vm_name_new']}"
            )
        return vm

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

    def to_hypercore(self, hcversion: HyperCoreVersion):
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
        if self._power_action:
            vm_dict["state"] = FROM_ANSIBLE_TO_HYPERCORE_POWER_ACTION.get(
                self._power_action, "unknown-power-state-sorry"
            )

        if self.machine_type and hcversion.verify("<9.3.0"):
            vm_dict["machineType"] = VmMachineType.from_ansible_to_hypercore(
                self.machine_type, hcversion
            )

        return vm_dict

    def to_ansible(self):
        # state attribute is used by HC3 only during VM create.
        return dict(
            vm_name=self.name,
            description=self.description,
            operating_system=self.operating_system,
            power_state=self._power_state,
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
            replication_source_vm_uuid=self.replication_source_vm_uuid,
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
        hcversion = HyperCoreVersion(rest_client)
        payload = self.to_hypercore(hcversion)
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
        if hcversion.verify(">=9.3.0"):
            if self.machine_type:
                machine_type_keyword = (
                    VmMachineType.from_ansible_to_hypercore_machine_type_keyword(
                        self.machine_type
                    )
                )
                options.update(dict(machineTypeKeyword=machine_type_keyword))
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
            (
                nic["vlan_new"]
                if ("vlan_new" in nic.keys() and nic["vlan_new"])
                else nic["vlan"]
            )
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
        if self.replication_source_vm_uuid:
            # The VM represented by self is a replication target VM.
            # Do restore from the latest snapshot.
            # We always have at least one shapshot available.
            # But it takes a while for a snapshot to transfer.
            source_snapshot_uuid = self.snapshot_uuids[-1]
        else:
            # The VM represented by self is a regular VM.
            # We omit snapUUID from clone API payload, and HC3 will
            # first automatically create a snaphost,
            # then clone the snapshot into a new VM.
            source_snapshot_uuid = ansible_dict.get("hypercore_snapshot_uuid")
        data = VM.create_clone_vm_payload(
            ansible_dict["vm_name"],
            ansible_dict["tags"],
            self.tags,
            cloud_init_data,
            preserve_mac_address=ansible_dict["preserve_mac_address"],
            source_nics=self.nics,
            source_snapshot_uuid=source_snapshot_uuid,
        )
        return rest_client.create_record(
            endpoint=f"/rest/v1/VirDomain/{self.uuid}/clone",
            payload=data,
            check_mode=False,
            timeout=None,
        )

    def __eq__(self, other: "VM"):
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
                self._power_state == other._power_state,
                self._power_action == other._power_action,
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
        # to_hypercore() needs HcVersion, we do not have it
        return str(dict(ansible=self.to_ansible()))

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
            raise errors.ScaleComputingError(
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

    def update_vm_power_state(
        self, module, rest_client, desired_power_action, ignore_repeated_request: bool
    ):
        """Sets the power state to what is stored in self.power_state"""

        # desired_power_action must be present in FROM_ANSIBLE_TO_HYPERCORE_POWER_ACTION's keys
        def assert_or_ignore_repeated_request(msg):
            if ignore_repeated_request:
                # Do not start/stop/shutdown VM twice.
                # Normally we want to assert if a second start/stop/shutdown is tried.
                # But as very last module change it makes sense to push VM into requested power_state,
                # without knowing what did module already do with VM power_state.
                # So in this special case, allow a second call, and just silently ignore
                # it if VM power_state was already set to desired state.
                return
            else:
                raise AssertionError(msg)

        if not self._power_state:
            raise errors.ScaleComputingError("No information about VM's power state.")

        # keep a record what was done
        if desired_power_action == "start":
            if self._was_start_tried:
                return assert_or_ignore_repeated_request(
                    "VM _was_start_tried already set"
                )
            self._was_start_tried = True
        if desired_power_action == "shutdown":
            if self._was_nice_shutdown_tried:
                return assert_or_ignore_repeated_request(
                    "VM _was_nice_shutdown_tried already set"
                )
            self._was_nice_shutdown_tried = True
        if desired_power_action == "stop":
            if self._was_force_shutdown_tried:
                return assert_or_ignore_repeated_request(
                    "VM _was_force_shutdown_tried already set"
                )
            self._was_force_shutdown_tried = True
        if desired_power_action == "reboot":
            if self._was_reboot_tried:
                return assert_or_ignore_repeated_request(
                    "VM _was_reboot_tried already set"
                )
            self._was_reboot_tried = True
        if desired_power_action == "reset":
            if self._was_reset_tried:
                return assert_or_ignore_repeated_request(
                    "VM _was_reset_tried already set"
                )
            self._was_reset_tried = True

        try:
            task_tag = rest_client.create_record(
                "/rest/v1/VirDomain/action",
                [
                    dict(
                        virDomainUUID=self.uuid,
                        actionType=FROM_ANSIBLE_TO_HYPERCORE_POWER_ACTION[
                            desired_power_action
                        ],
                        cause="INTERNAL",
                    )
                ],
                module.check_mode,
            )
        except errors.UnexpectedAPIResponse as ex:
            if desired_power_action != "reset":
                raise
            # We are allowed to send reset only if VM is in
            # RUNNING or SHUTDOWN (as in middle of shutting down, but not yet fully shutdown).
            # If VM is already shutoff, the request fails.
            # Ignore this special case.
            # The whole RESET is not even exposed on HyperCore UI,
            # maybe we should remove it from ansible.
            if ex.response_status != 500:
                # the '500 b'{"error":"An internal error occurred"}'' is the one to ignore
                raise
            module.warn("Ignoring failed VM RESET")
            return
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
        raise errors.ScaleComputingError(
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
        if module.params["force_reboot"] and self._was_nice_shutdown_tried:
            self.update_vm_power_state(module, rest_client, "stop", False)
            # force shutdown should always work. If not, we need to pool for state change.
            # Maybe we need to pool for state change anyway -
            # TaskTag might be finished before VM is really off.
            # self._did_force_shutdown_work = True
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
            # and module.params["shutdown_timeout"]  # default is 300 anyway
            and not self._was_nice_shutdown_tried
        ):
            self.update_vm_power_state(module, rest_client, "shutdown", False)
            shutdown_timeout = module.params["shutdown_timeout"]
            start = time()
            while 1:
                vm = rest_client.get_record(
                    f"/rest/v1/VirDomain/{self.uuid}", must_exist=True
                )
                current_time = time() - start
                if vm["state"] in ["SHUTDOWN", "SHUTOFF"]:
                    self._did_nice_shutdown_work = True
                    return True
                if current_time >= shutdown_timeout:
                    return False
                sleep(10)
        return False

    def vm_power_up(self, module, rest_client):
        # Powers up a VM in case:
        #   - VM was shutdown during module execution or
        #   - started/running state was explicitly requested (by module param power_state).
        # But: VM is not started if
        #   - VM was initially stopped and
        #   - module param power_state is omitted or contains "stop".
        if self.was_vm_shutdown() and self._initially_running:
            self.update_vm_power_state(module, rest_client, "start", False)
            return
        # Also start VM if module power_state requires a power on.
        # Field _power_action is set only if VM instance was created with from_ansible();
        # it is None if VM instance was created with from_hypercore().
        requested_power_action = module.params.get("power_state")
        if requested_power_action == "start":
            self.update_vm_power_state(module, rest_client, "start", False)

    def was_vm_shutdown(self) -> bool:
        """

        Returns: True if VM was shutdown (nice ACPI, or force).
        """
        return any([self._did_nice_shutdown_work, self._was_force_shutdown_tried])

    def was_vm_rebooted(self) -> bool:
        # Now, VM was rebooted when it was running at start, then stopped and powered on:
        # Assume we did not try to shutdown/stop a stopped VM.
        # We assume VM start did work (there are cases when VM is not bootable - like UEFI without NVRAM disk).
        vm_rebooted = self.was_vm_shutdown() and self._was_start_tried
        return vm_rebooted

    def do_shutdown_steps(self, module, rest_client):
        if not self.wait_shutdown(module, rest_client):
            if not self.vm_shutdown_forced(module, rest_client):
                raise errors.ScaleComputingError(
                    f"VM - {self.name} - needs to be powered off and is not responding to a shutdown request."
                )

    def check_vm_before_create(self):
        # UEFI machine type must have NVRAM disk.
        disk_type_list = [disk.type for disk in self.disks]
        if self.machine_type == "UEFI" and "nvram" not in disk_type_list:
            raise errors.ScaleComputingError(
                "Machine of type UEFI requires NVRAM disk."
            )
        # vTPM+UEFI machine type must have NVRAM and VTPM disks.
        # This in not implemented yet, since this version of API does not support VTPM.
        if (
            # TODO -compatible type is missing
            self.machine_type == "vTPM+UEFI"
            and "nvram" not in disk_type_list
            and "vtpm" not in disk_type_list
        ):
            raise errors.ScaleComputingError(
                "Machine of type vTPM+UEFI requires NVRAM disk and VTPM disk."
            )


class ManageVMParams(VM):
    @staticmethod
    def _build_payload(module, rest_client):
        payload = {}
        if module.params["operating_system"]:
            payload["operatingSystem"] = module.params["operating_system"]
        if module.params["vm_name_new"]:
            payload["name"] = module.params["vm_name_new"]
        if module.params["description"] is not None:  # we want to be able to write ""
            payload["description"] = module.params["description"]
        if module.params["tags"] is not None:  # we want to be able to write ""
            payload["tags"] = ",".join(
                module.params["tags"]
            )  # tags is a list of strings
        if module.params["memory"] is not None:
            payload["mem"] = module.params["memory"]
        if module.params["vcpu"] is not None:
            payload["numVCPU"] = module.params["vcpu"]
        if module.params.get("machine_type") is not None:
            # On create/POST, machineTypeKeyword can be used (if HC3>=9.3.0).
            # On update/PATCH, machineTypeKeyword cannot be used (tested with HC3 9.3.5).
            hcversion = HyperCoreVersion(rest_client)
            hc3_machine_type = VmMachineType.from_ansible_to_hypercore(
                module.params["machine_type"], hcversion
            )
            payload["machineType"] = hc3_machine_type
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
    def _needs_reboot(module, changed_parameters: dict[str, bool]):
        """

        Args:
            module: ansible module
            changed: Contains list of parameter names that were changed

        Returns: True if (at least one) parameter change requires VM reboot.

        """
        for param_name in module.params:
            if (
                module.params[param_name] is not None and param_name in REBOOT_LOOKUP
            ):  # skip not provided parameters and cluster_instance
                if REBOOT_LOOKUP[param_name] and changed_parameters.get(param_name):
                    return True
        return False

    @staticmethod
    def _to_be_changed(vm, module, param_subset: List[str]):
        changed_params = {}
        if module.params["vm_name_new"]:
            changed_params["vm_name"] = vm.name != module.params["vm_name_new"]
        if module.params["operating_system"]:
            changed_params["operating_system"] = (
                vm.operating_system != module.params["operating_system"]
            )
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
            # is in FROM_ANSIBLE_TO_HYPERCORE_POWER_ACTION.keys(), whereas vm.power_state
            # is in FROM_HYPERCORE_TO_ANSIBLE_POWER_STATE.values().
            # state in playbook is different than read from HC3 (start/started)
            # E.g. "start" in "started", "stop" in "stopped".
            # TODO double check if text above is still true
            # is_substring = module.params["power_state"] not in vm._power_action
            # changed_params["power_state"] = is_substring
            # q(module.params["power_state"], vm._power_state, vm._power_action, changed_params["power_state"])

            # vm._power_state describes actual state from HC3.
            # module.params["power_state"] is ansible power_action, describing desired state.
            requested_power_action = module.params["power_state"]
            if requested_power_action in ["reset", "reboot"]:
                # "reset" and "reboot" needs to be applied always.
                changed_params["power_state"] = True
            else:
                desired_power_state = FROM_ANSIBLE_POWER_ACTION_TO_ANSIBLE_POWER_STATE[
                    requested_power_action
                ]
                changed_params["power_state"] = desired_power_state != vm._power_state

        if module.params.get("machine_type") is not None:
            changed_params["machine_type"] = (
                vm.machine_type != module.params["machine_type"]
            )
        if (
            module.params["snapshot_schedule"] is not None
        ):  # we want to be able to write ""
            changed_params["snapshot_schedule"] = (
                vm.snapshot_schedule != module.params["snapshot_schedule"]
            )

        if param_subset:
            # Caller can decide to change only subset of all needed changes.
            # This allows applying a change in two steps.
            changed_params_filtered = {
                param_name: changed_params[param_name]
                for param_name in param_subset
                if param_name in changed_params
            }
        else:
            changed_params_filtered = changed_params

        return any(changed_params_filtered.values()), changed_params_filtered

    @staticmethod
    def _build_after_diff(module, rest_client):
        after = {}
        if module.check_mode:
            if module.params["operating_system"]:
                after["operating_system"] = module.params["operating_system"]
            if module.params["vm_name_new"]:
                after["vm_name"] = module.params["vm_name_new"]
            if module.params["description"] is not None:
                after["description"] = module.params["description"]
            if module.params["tags"] is not None:
                after["tags"] = module.params["tags"]
            if module.params["memory"] is not None:
                after["memory"] = module.params["memory"]
            if module.params["vcpu"] is not None:
                after["vcpu"] = module.params["vcpu"]
            if module.params["power_state"]:
                after["power_state"] = module.params["power_state"]
            if module.params["snapshot_schedule"] is not None:
                after["snapshot_schedule"] = module.params["snapshot_schedule"]
            return after

        query = {
            "name": (
                module.params["vm_name_new"]
                if module.params["vm_name_new"]
                else module.params["vm_name"]
            )
        }
        vm = VM.get_or_fail(query, rest_client)[0]
        if module.params["operating_system"]:
            after["operating_system"] = vm.operating_system
        if module.params["vm_name_new"]:
            after["vm_name"] = vm.name
        if module.params["description"] is not None:
            after["description"] = vm.description
        if module.params["tags"] is not None:
            after["tags"] = vm.tags
        if module.params["memory"] is not None:
            after["memory"] = vm.mem
        if module.params["vcpu"] is not None:
            after["vcpu"] = vm.numVCPU
        if module.params["power_state"]:
            after["power_state"] = vm._power_state
        if module.params["snapshot_schedule"] is not None:
            after["snapshot_schedule"] = vm.snapshot_schedule
        return after

    @staticmethod
    def _build_before_diff(vm, module):
        before = {}
        if module.params["operating_system"]:
            before["operating_system"] = vm.operating_system
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
            before["power_state"] = vm._power_state
        if module.params["snapshot_schedule"] is not None:
            before["snapshot_schedule"] = vm.snapshot_schedule
        return before

    @classmethod
    def set_vm_params(cls, module, rest_client, vm, param_subset: List[str]):
        changed, changed_parameters = ManageVMParams._to_be_changed(
            vm, module, param_subset
        )
        cls._check_if_required_disks_are_present(module, vm, changed_parameters)

        if changed:
            payload = ManageVMParams._build_payload(module, rest_client)
            endpoint = "{0}/{1}".format("/rest/v1/VirDomain", vm.uuid)
            task_tag = rest_client.update_record(endpoint, payload, module.check_mode)
            TaskTag.wait_task(rest_client, task_tag)

            # shutdown VM if it needs to be rebooted to apply NIC/disk changes
            if ManageVMParams._needs_reboot(
                module, changed_parameters
            ) and vm._power_action not in ["stop", "stopped", "shutdown"]:
                vm.do_shutdown_steps(module, rest_client)

            return (
                True,
                dict(
                    before=ManageVMParams._build_before_diff(vm, module),
                    after=ManageVMParams._build_after_diff(module, rest_client),
                ),
                changed_parameters,
            )
        else:
            return (
                False,
                dict(before=None, after=None),
                changed_parameters,
            )

    @classmethod
    def _check_if_required_disks_are_present(
        cls, module, vm, changed_parameters: dict[str, bool]
    ):
        if "machine_type" in changed_parameters:
            # Changing machineType can make VM unbootable (from BIOS to UEFI, without NVRAM disk).
            # After boot is tried, VM does not boot, type cannot be changed back, and support is needed.
            # Prevent that.
            if module.params["machine_type"] == "BIOS":
                nvram_needed = False
                vtpm_needed = False
            elif module.params["machine_type"] == "UEFI":
                nvram_needed = True
                vtpm_needed = False
            elif module.params["machine_type"] in ["vTPM+UEFI", "vTPM+UEFI-compatible"]:
                nvram_needed = True
                vtpm_needed = True
            else:
                raise AssertionError(
                    f"machine_type={module.params['machine_type']} not included in set_vm_params."
                )
            # At end of module execution we will have VM with final_disks.
            if "disks" in module.params:
                # vm module, "disks" param was passed
                final_disks = [
                    Disk.from_ansible(disk) for disk in module.params["disks"]
                ]
            else:
                # vm_params has no disks, we need to check the actual VM disks
                final_disks = vm.disks
            nvram_disks = [disk for disk in final_disks if disk.type == "nvram"]
            vtpm_disks = [disk for disk in final_disks if disk.type == "vtpm"]
            fail_message_requirements = []
            if nvram_needed and not nvram_disks:
                fail_message_requirements.append("nvram disk")
            if vtpm_needed and not vtpm_disks:
                fail_message_requirements.append("vtpm disk")
            if fail_message_requirements:
                fail_details = ", ".join(fail_message_requirements)
                module.fail_json(
                    f"Changing machineType to {module.params['machine_type']} requires {fail_details}."
                )


class ManageVMDisks:
    @staticmethod
    def get_vm_by_name(module, rest_client):
        """
        Wrapps VM's method get_by_name. Additionally, it raises exception if vm isn't found
        Returns vm object and list of ansible disks (this combo is commonly used in this module).
        """
        # If there's no VM with such name, error is raised automatically
        vm = VM.get_by_old_or_new_name(module.params, rest_client, must_exist=True)
        return vm, [disk.to_ansible() for disk in vm.disks]

    @staticmethod
    def _create_block_device(module, rest_client, vm, desired_disk):
        # vm is instance of VM, desired_disk is instance of Disk
        payload = desired_disk.post_and_patch_payload(vm, None)
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
    def _update_block_device(
        module, rest_client, desired_disk, existing_disk: Disk, vm
    ):
        payload = desired_disk.post_and_patch_payload(vm, existing_disk)
        if existing_disk.needs_reboot("update", desired_disk):
            vm.do_shutdown_steps(module, rest_client)
        task_tag = rest_client.update_record(
            "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", existing_disk.uuid),
            payload,
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag, module.check_mode)

    @classmethod
    def _delete_not_used_disks(cls, module, rest_client, vm, changed, disk_key):
        updated_vm, updated_ansible_disks = cls.get_vm_by_name(module, rest_client)
        # Ensure all disk that aren't listed in items don't exist in VM (ensure absent)
        for updated_ansible_disk in updated_ansible_disks:
            existing_disk = Disk.from_ansible(updated_ansible_disk)
            to_delete = True
            # Ensure idempotence with cloud-init and guest-tools IDE_DISKs
            if existing_disk.name and (
                "cloud-init" in existing_disk.name
                or "guest-tools" in existing_disk.name
            ):
                continue
            for ansible_desired_disk in module.params[disk_key]:
                desired_disk = Disk.from_ansible(ansible_desired_disk)
                if (
                    desired_disk.slot == existing_disk.slot
                    and desired_disk.type == existing_disk.type
                ):
                    to_delete = False
            if to_delete:
                # HyperCore is sometimes able to delete disk on running VM,
                # but sometimes we need to shutdown VM to remove disk.
                # It is hard to know in advance if shutdown is required.
                # We try to remove disk without shutdown, if delete fails, we shutdown VM and try again.
                if existing_disk.needs_reboot("delete"):
                    vm.do_shutdown_steps(module, rest_client)
                task_tag = rest_client.delete_record(
                    "{0}/{1}".format(
                        "/rest/v1/VirDomainBlockDevice", existing_disk.uuid
                    ),
                    module.check_mode,
                )
                try:
                    TaskTag.wait_task(rest_client, task_tag, module.check_mode)
                except errors.TaskTagError as ex:
                    # Delete failed, maybe because VM was running and disk was in use.
                    # If VM is running, shutdown VM and retry delete.
                    if ex.task_status_state != "ERROR":
                        raise
                    if not cls._disk_remove_failed_because_vm_running(ex.task_status):
                        raise
                    vm_fresh_data = rest_client.get_record(
                        f"/rest/v1/VirDomain/{vm.uuid}", must_exist=True
                    )
                    if vm_fresh_data["state"] != "RUNNING":
                        raise
                    # shutdown and retry remove
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
    def _disk_remove_failed_because_vm_running(task_status: Dict):
        # Look at task_tag dict returned by HyperCore to decide if disk remove failed
        # because VM is running, and VM shutdown will allow us to remove the disk.
        # What we search for in formattedMessage is HyperCore version dependent:
        #   9.2.17 - "Unable to delete block device from VM '%@': Still in use"
        #   9.1.14 - "Virt Exception, code: 84, domain 10: Operation not supported: This type of disk cannot be hot unplugged"

        if (
            task_status["formattedMessage"]
            == "Unable to delete block device from VM '%@': Still in use"
        ):
            return True
        if task_status["formattedMessage"].endswith(
            "Operation not supported: This type of disk cannot be hot unplugged"
        ):
            return True
        return False

    @staticmethod
    def _force_remove_all_disks(module, rest_client, vm, disks_before):
        # It's important to check if items is equal to empty list and empty list only (no None-s)
        # This method is going to be called in vm_disk class only.
        if module.params["items"] != []:
            raise errors.ScaleComputingError(
                "If force set to true, items should be set to empty list"
            )
        # Delete all disks
        for existing_disk in vm.disks:
            task_tag = rest_client.delete_record(
                "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", existing_disk.uuid),
                module.check_mode,
            )
            TaskTag.wait_task(rest_client, task_tag, module.check_mode)
        return True, [], dict(before=disks_before, after=[]), False

    @classmethod
    def ensure_present_or_set(cls, module, rest_client, module_path, vm_before: VM):
        # At the moment, this method is called in modules vm_disk and vm
        # Module path is here to distinguish from which module ensure_present_or_set was called from
        changed = False
        called_from_vm_disk = not VM.called_from_vm_module(module_path)
        disk_key = "items" if called_from_vm_disk else "disks"
        # vm_before, disks_before = cls.get_vm_by_name(module, rest_client)
        disks_before = [disk.to_ansible() for disk in vm_before.disks]
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
            if (
                ansible_existing_disk
                and "size" in ansible_desired_disk
                and ansible_desired_disk["size"] is not None
                and ansible_existing_disk["size"] > ansible_desired_disk["size"]
            ):
                raise errors.ScaleComputingError(
                    "Disk size can only be enlarged, never downsized."
                )
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
                    # Empty CD-ROM is requested. Detach ISO if needed.
                    if ansible_existing_disk:
                        name = ansible_existing_disk["iso_name"]  #
                        existing_iso = ISO.get_by_name(
                            dict(name=name), rest_client, must_exist=False
                        )
                        if existing_iso:
                            cls.iso_image_management(
                                module, rest_client, existing_iso, uuid, attach=False
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

                    if existing_disk.type == "nvram":
                        # Special case: nvram disk, PATCH cannot change the size/capacity
                        # See also Disk.post_and_patch_payload
                        ansible_desired_disk_filtered["size"] = ansible_existing_disk[
                            "size"
                        ]

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
            vm_before.vm_power_up(module, rest_client)
            vm_after, disks_after = cls.get_vm_by_name(module, rest_client)
            return (
                changed,
                disks_after,
                dict(before=disks_before, after=disks_after),
                vm_before.was_vm_rebooted(),
            )
        return changed


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
        TaskTag.wait_task(rest_client=rest_client, task=response)
        new_nic_obj = ManageVMNics.get_by_uuid(
            rest_client=rest_client, nic_uuid=existing_nic.uuid
        )
        after.append(new_nic_obj.to_ansible())
        return True, before, after

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
        TaskTag.wait_task(rest_client=rest_client, task=response)
        new_nic_obj = ManageVMNics.get_by_uuid(
            rest_client=rest_client, nic_uuid=response["createdUUID"]
        )
        after.append(new_nic_obj.to_ansible())
        return True, before, after

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
        TaskTag.wait_task(rest_client=rest_client, task=response)
        after.append(None)
        return True, before, after

    @classmethod
    def ensure_present_or_set(cls, module, rest_client, module_path, vm_before: VM):
        """

        Args:
            module:
            rest_client:
            module_path:
            vm_before: The VM matching vm_name/vm_name_new

        Returns:
            changed:
            before:
            after:
            reboot: bool, it means reboot required if VM was running before.
        """
        before = []
        after = []
        changed = False
        called_from_vm_nic = not VM.called_from_vm_module(module_path)
        nic_key = "items" if called_from_vm_nic else "nics"
        if module.params[nic_key]:
            for nic in module.params[nic_key]:
                nic["vm_uuid"] = vm_before.uuid
                nic = Nic.from_ansible(ansible_data=nic)
                existing_hc3_nic, existing_hc3_nic_with_new = vm_before.find_nic(
                    vlan=nic.vlan,
                    mac=nic.mac,
                    vlan_new=nic.vlan_new,
                    mac_new=nic.mac_new,
                )
                if existing_hc3_nic_with_new and Nic.is_update_needed(
                    existing_hc3_nic_with_new, nic
                ):  # Update existing with vlan_new or mac_new - corner case
                    (
                        changed_tmp,
                        before,
                        after,
                    ) = ManageVMNics.send_update_nic_request_to_hypercore(
                        module,
                        vm_before,
                        rest_client,
                        nic,
                        existing_hc3_nic_with_new,
                        before,
                        after,
                    )
                    changed = changed or changed_tmp
                elif (
                    existing_hc3_nic  # Nic
                    and not existing_hc3_nic_with_new  # None
                    and Nic.is_update_needed(existing_hc3_nic, nic)  # True
                ):  # Update existing
                    (
                        changed_tmp,
                        before,
                        after,
                    ) = ManageVMNics.send_update_nic_request_to_hypercore(
                        module,
                        vm_before,
                        rest_client,
                        nic,
                        existing_hc3_nic,
                        before,
                        after,
                    )
                    changed = changed or changed_tmp
                # Create new
                elif not existing_hc3_nic and not existing_hc3_nic_with_new:
                    (
                        changed_tmp,
                        before,
                        after,
                    ) = ManageVMNics.send_create_nic_request_to_hypercore(
                        module,
                        vm_before,
                        rest_client=rest_client,
                        new_nic=nic,
                        before=before,
                        after=after,
                    )
                    changed = changed or changed_tmp
        elif module.params[nic_key] == []:  # empty set in ansible, delete all
            for nic in vm_before.nic_list:
                before.append(nic.to_ansible())
        else:
            raise errors.MissingValueAnsible(
                "items, cannot be null, empty must be set to []"
            )

        # If the only change is to delete a NIC, then
        # the vm_before would not know VM was shutdown and reboot is needed.
        # The delete_unused_nics_to_hypercore_vm() must get updated VLANs.
        updated_virtual_machine_TEMP = VM.get_by_old_or_new_name(
            module.params, rest_client=rest_client
        )
        updated_virtual_machine = vm_before
        updated_virtual_machine.nics = updated_virtual_machine_TEMP.nics
        del updated_virtual_machine_TEMP
        # TODO are nics from vm_before used anywhere?

        if module.params["state"] == NicState.set or not called_from_vm_nic:
            # Check if any nics need to be deleted from the vm
            changed_tmp = updated_virtual_machine.delete_unused_nics_to_hypercore_vm(
                module, rest_client, nic_key
            )
            changed = changed or changed_tmp
        if called_from_vm_nic:
            return (
                changed,
                after,
                dict(before=before, after=after),
            )
        return changed
