# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils import errors
from ..module_utils.rest_client import RestClient
from typing import Optional, Any


TIERING_PRIORITY_MAPPING_TO_HYPERCORE = {
    0: 0,
    1: 1,
    2: 2,
    3: 4,
    4: 8,
    5: 16,
    6: 32,
    7: 64,
    8: 128,
    9: 256,
    10: 1024,
    11: 10240,
}
TIERING_PRIORITY_MAPPING_FROM_HYPERCORE = {
    0: 0,
    1: 1,
    2: 2,
    4: 3,
    8: 4,
    16: 5,
    32: 6,
    64: 7,
    128: 8,
    256: 9,
    1024: 10,
    10240: 11,
}
# default tiering priority is 8 on HyperCore side == 4 in ansible
TIERING_PRIORITY_DEFAULT = 4


class Disk(PayloadMapper):
    def __init__(
        self,
        type,
        slot,
        uuid=None,
        vm_uuid=None,
        cache_mode=None,
        size=None,
        name=None,
        disable_snapshotting=None,
        tiering_priority_factor=None,
        mount_points=None,
        read_only=None,
    ):
        self.uuid = uuid
        self.vm_uuid = vm_uuid
        self.type = type
        self.cache_mode = cache_mode
        self.size = size
        self.slot = slot
        self.name = name
        self.disable_snapshotting = disable_snapshotting
        self.tiering_priority_factor = tiering_priority_factor
        self.mount_points = mount_points
        self.read_only = read_only

    def to_hypercore(self):
        return dict(
            virDomainUUID=self.vm_uuid,
            type=self.type.upper(),
            cacheMode=self.cache_mode.upper() if self.cache_mode else None,
            capacity=self.size,
            slot=self.slot,
            name=self.name,
            disableSnapshotting=self.disable_snapshotting,
            tieringPriorityFactor=(
                TIERING_PRIORITY_MAPPING_TO_HYPERCORE[self.tiering_priority_factor]
                if self.tiering_priority_factor is not None
                else None
            ),
            mountPoints=self.mount_points,
            readOnly=self.read_only,
        )

    def to_ansible(self):
        return dict(
            uuid=self.uuid,
            vm_uuid=self.vm_uuid,
            type=self.type,
            cache_mode=self.cache_mode,
            size=self.size,
            disk_slot=self.slot,
            iso_name=self.name,
            disable_snapshotting=self.disable_snapshotting,
            tiering_priority_factor=self.tiering_priority_factor,
            mount_points=self.mount_points,
            read_only=self.read_only,
        )

    @classmethod
    def from_hypercore(cls, hypercore_data: dict[Any, Any]) -> Optional[Disk]:
        if not hypercore_data:
            return None
        try:
            return cls(
                uuid=hypercore_data["uuid"],
                vm_uuid=hypercore_data["virDomainUUID"],
                type=hypercore_data["type"].lower(),
                cache_mode=hypercore_data["cacheMode"].lower(),
                size=hypercore_data["capacity"],
                slot=hypercore_data["slot"],
                name=hypercore_data["name"],
                disable_snapshotting=hypercore_data["disableSnapshotting"],
                # Hypercore sometimes returns values outside the mapping table, so we set it to default.
                tiering_priority_factor=(
                    TIERING_PRIORITY_MAPPING_FROM_HYPERCORE[
                        hypercore_data["tieringPriorityFactor"]
                    ]
                    if hypercore_data["tieringPriorityFactor"]
                    in TIERING_PRIORITY_MAPPING_FROM_HYPERCORE
                    else TIERING_PRIORITY_DEFAULT
                ),
                mount_points=hypercore_data["mountPoints"],
                read_only=hypercore_data["readOnly"],
            )
        except KeyError as e:
            raise errors.MissingValueHypercore(e)

    @classmethod
    def from_ansible(cls, ansible_data):
        # Specific for this module - in case of performing PATCH method on the /VirDomainBlockDevice endpoint,
        # type_new is possible field if you want to update disk type. In that case, type_new is desired type
        # of the disk
        if ansible_data.get("type_new", ""):
            disk_type = ansible_data["type_new"]
        else:
            disk_type = ansible_data["type"]
        # Only disk_type and slot are certainly going to be present in hypercore_data.
        # The rest of the fields may be specified if update action is performed
        # Ensure that size is integer
        if ansible_data.get("size", None):
            size = int(ansible_data["size"])
        else:
            size = None
        return cls(
            type=disk_type,
            slot=ansible_data["disk_slot"],
            size=size,
            cache_mode=ansible_data.get("cache_mode", None),
            name=ansible_data.get("iso_name", None),
            disable_snapshotting=ansible_data.get("disable_snapshotting", None),
            tiering_priority_factor=ansible_data.get("tiering_priority_factor", None),
            mount_points=ansible_data.get("mount_points", None),
            read_only=ansible_data.get("read_only", None),
            uuid=ansible_data.get("uuid", None),  # Needed in delete disk
        )

    def __eq__(self, other):
        """One Disk is equal to another if it has ALL attributes exactly the same. Used in tests only."""
        return all(
            (
                self.uuid == other.uuid,
                self.vm_uuid == other.vm_uuid,
                self.type == other.type,
                self.cache_mode == other.cache_mode,
                self.size == other.size,
                self.slot == other.slot,
                self.name == other.name,
                self.disable_snapshotting == other.disable_snapshotting,
                self.tiering_priority_factor == other.tiering_priority_factor,
                self.mount_points == other.mount_points,
                self.read_only == other.read_only,
            )
        )

    def __str__(self):
        return super().__str__()

    def post_and_patch_payload(self, vm, existing_disk: Disk):
        # vm is instance of class VM
        # vm will always have uuid property in the playbook
        payload = dict(
            {key: val for key, val in self.to_hypercore().items() if val is not None},
            virDomainUUID=vm.uuid,
        )
        # Special case - NVRAM disk
        # HyperCore will ignore provided slot, and will set slot=-1.
        # Similar for size/capacity, nvram has size 540672 B (at least on HC3 9.2.22).
        # Capacity field is required for POST, but it cannot be changed with PATCH.
        if self.type == "nvram":
            payload.pop("slot", None)
            if existing_disk and payload.get("capacity"):
                payload["capacity"] = existing_disk.size
        # Special case - VTPM disk
        # HyperCore will ignore provided slot, and will set slot=-1.
        # The size/capacity is respected.
        if self.type == "vtpm":
            payload.pop("slot", None)
        return payload

    def needs_reboot(self, action: str, desired_disk=None) -> bool:
        # action is "create", "update", "delete".
        # Only a few actions over disks require reboot.
        # Delete and change type.
        if desired_disk and action == "update" and self.type != desired_disk.type:
            return True
        if action == "delete" and self.type == "ide_cdrom":
            # ide_cdrom can never be deleted when VM is running.
            # Also other disks types cannot be deleted when VM is running
            # if HyperCore thinks disk is being "used".
            return True
        return False

    @classmethod
    def get_by_uuid(
        cls, uuid: str, rest_client: RestClient, must_exist: bool
    ) -> Optional[Disk]:
        hypercore_dict = rest_client.get_record(
            f"/rest/v1/VirDomainBlockDevice/{uuid}", must_exist=must_exist
        )
        return cls.from_hypercore(hypercore_dict)
