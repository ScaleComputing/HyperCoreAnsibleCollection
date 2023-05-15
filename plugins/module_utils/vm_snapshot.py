# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from copy import copy

from .rest_client import RestClient

from ..module_utils.utils import PayloadMapper
from ..module_utils.errors import ScaleComputingError
from ..module_utils.vm import VM
from ..module_utils import errors

from ..module_utils.typed_classes import (
    TypedVMSnapshotToAnsible,
    TypedVMSnapshotFromAnsible,
    TypedTaskTag,
)
from typing import List, Any, Dict, Optional
import time
import datetime


class VMSnapshot(PayloadMapper):
    def __init__(
        self,
        snapshot_uuid: Optional[str] = None,
        vm_name: Optional[str] = None,
        vm: Optional[Dict[Any, Any]] = None,
        domain: Optional[VM] = None,
        device_snapshots: Optional[List[Dict[Any, Any]]] = None,
        timestamp: Optional[int] = None,
        label: Optional[str] = None,
        type: Optional[str] = None,
        automated_trigger_timestamp: Optional[int] = None,
        local_retain_until_timestamp: Optional[float] = None,
        remote_retain_until_timestamp: Optional[float] = None,
        retain_for: Optional[int] = None,
        block_count_diff_from_serial_number: Optional[int] = None,
        replication: Optional[bool] = True,
    ):
        self.snapshot_uuid = snapshot_uuid if snapshot_uuid is not None else ""
        self.vm = vm if vm is not None else {}
        self.vm_name = vm_name
        self.domain = domain
        self.device_snapshots = device_snapshots if device_snapshots is not None else []
        self.timestamp = timestamp
        self.label = label
        self.type = type
        self.automated_trigger_timestamp = automated_trigger_timestamp
        self.local_retain_until_timestamp = local_retain_until_timestamp
        self.remote_retain_until_timestamp = remote_retain_until_timestamp
        self.retain_for = retain_for
        self.block_count_diff_from_serial_number = block_count_diff_from_serial_number
        self.replication = replication

    @staticmethod
    def convert_to_unix_timestamp(date: Optional[datetime.date]) -> Optional[float]:
        # Date format: 'YYYY-MM-DD hh:mm:ss'
        # Example: '2023-04-24 10:03:00'
        if date:
            return time.mktime(datetime.datetime.timetuple(date))
        return None

    @staticmethod
    def convert_from_unix_timestamp(
        unix_timestamp: Optional[float],
    ) -> Optional[datetime.date]:
        # Unix format: 1584101485
        if unix_timestamp:
            return datetime.datetime.fromtimestamp(unix_timestamp)
        return None

    @staticmethod
    def calculate_date(days: Optional[int]) -> Optional[float]:
        if days is None or days == 0:
            return None
        return VMSnapshot.convert_to_unix_timestamp(
            datetime.datetime.today() + datetime.timedelta(days=days)
        )

    @classmethod
    def from_ansible(cls, ansible_data: TypedVMSnapshotFromAnsible) -> VMSnapshot:
        retain_timestamp = cls.calculate_date(ansible_data.get("retain_for"))
        return cls(
            vm_name=ansible_data["vm_name"],
            label=ansible_data["label"],
            local_retain_until_timestamp=retain_timestamp,
            remote_retain_until_timestamp=retain_timestamp,
            replication=ansible_data["replication"],
            retain_for=ansible_data.get("retain_for"),
        )

    @classmethod
    def from_hypercore(
        cls, hypercore_data: Optional[Dict[Any, Any]]
    ) -> Optional[VMSnapshot]:
        if not hypercore_data:
            return None
        return cls(
            snapshot_uuid=hypercore_data["uuid"],
            vm_name=hypercore_data["domain"]["name"],
            vm={
                "name": hypercore_data["domain"]["name"],
                "uuid": hypercore_data["domainUUID"],
                "snapshot_serial_number": hypercore_data["domain"][
                    "snapshotSerialNumber"
                ],
                "disks": [
                    {
                        "uuid": disk["uuid"],
                        "type": disk["type"].lower(),
                        "disk_slot": disk["slot"],
                        "iso_name": disk["name"],
                        "cache_mode": disk["cacheMode"].lower(),
                        "size": disk["capacity"],
                        "disable_snapshotting": disk["disableSnapshotting"],
                        "tiering_priority_factor": disk["tieringPriorityFactor"],
                        "read_only": disk["readOnly"],
                    }
                    for disk in hypercore_data["domain"]["blockDevs"]
                ],
            },
            device_snapshots=[
                {"uuid": device_snapshot["uuid"]}
                for device_snapshot in hypercore_data["deviceSnapshots"]
            ],
            timestamp=hypercore_data["timestamp"],
            label=hypercore_data["label"],
            type=hypercore_data["type"],
            automated_trigger_timestamp=hypercore_data["automatedTriggerTimestamp"],
            local_retain_until_timestamp=hypercore_data["localRetainUntilTimestamp"],
            remote_retain_until_timestamp=hypercore_data["remoteRetainUntilTimestamp"],
            block_count_diff_from_serial_number=hypercore_data[
                "blockCountDiffFromSerialNumber"
            ],
            replication=hypercore_data["replication"],
        )

    def to_hypercore(self) -> Dict[Any, Any]:
        hypercore_dict = dict(
            uuid=self.snapshot_uuid,
            domainUUID=self.domain.uuid if self.domain else None,
            label=self.label,
            type=self.type
            or "USER",  # Currently we don't expose type; USER is default.
            replication=self.replication,
        )
        # Timestamps can't be set to None in the body.
        if self.local_retain_until_timestamp:
            hypercore_dict[
                "localRetainUntilTimestamp"
            ] = self.local_retain_until_timestamp
        if self.remote_retain_until_timestamp:
            hypercore_dict[
                "remoteRetainUntilTimestamp"
            ] = self.remote_retain_until_timestamp
        return hypercore_dict

    def to_ansible(self) -> TypedVMSnapshotToAnsible:
        return dict(
            snapshot_uuid=self.snapshot_uuid,
            vm_name=self.vm_name,
            vm=self.vm,
            device_snapshots=self.device_snapshots,
            timestamp=self.timestamp,
            label=self.label,
            type=self.type,
            automated_trigger_timestamp=self.automated_trigger_timestamp,
            local_retain_until_timestamp=self.convert_from_unix_timestamp(
                self.local_retain_until_timestamp
            ),
            remote_retain_until_timestamp=self.convert_from_unix_timestamp(
                self.remote_retain_until_timestamp
            ),
            block_count_diff_from_serial_number=self.block_count_diff_from_serial_number,
            replication=self.replication,
        )

    # This method is here for testing purposes!
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VMSnapshot):
            return NotImplemented

        check_vm = True  # it will stay True if self.vm == {}
        if self.vm != {}:
            vm_sorted_disks = sorted(self.vm["disks"], key=lambda disk: disk["iso_name"])  # type: ignore
            other_sorted_disks = sorted(other.vm["disks"], key=lambda disk: disk["iso_name"])  # type: ignore

            check_vm = all(
                (
                    self.vm["name"] == other.vm["name"],
                    self.vm["uuid"] == other.vm["uuid"],
                    self.vm["snapshot_serial_number"]
                    == other.vm["snapshot_serial_number"],
                    vm_sorted_disks == other_sorted_disks,
                )
            )

        return all(
            (
                self.snapshot_uuid == other.snapshot_uuid,
                check_vm,
                self.device_snapshots == other.device_snapshots,
                self.timestamp == other.timestamp,
                self.label == other.label,
                self.type == other.type,
                self.automated_trigger_timestamp == other.automated_trigger_timestamp,
                self.local_retain_until_timestamp == other.local_retain_until_timestamp,
                self.remote_retain_until_timestamp
                == other.remote_retain_until_timestamp,
                self.block_count_diff_from_serial_number
                == other.block_count_diff_from_serial_number,
                self.replication == other.replication,
            )
        )

    @classmethod
    def get_snapshot_by_uuid(
        cls, snapshot_uuid: str, rest_client: RestClient, must_exist: bool = False
    ) -> Optional[VMSnapshot]:
        hypercore_dict = rest_client.get_record(
            endpoint="/rest/v1/VirDomainSnapshot",
            query={"uuid": snapshot_uuid},
            must_exist=must_exist,
        )
        vm_snapshot = cls.from_hypercore(hypercore_dict)
        return vm_snapshot

    @classmethod
    def get_snapshots_by_query(
        cls,
        query: Dict[Any, Any],
        rest_client: RestClient,
    ) -> List[TypedVMSnapshotToAnsible]:
        snapshots = [
            cls.from_hypercore(hypercore_data=hypercore_dict).to_ansible()  # type: ignore
            for hypercore_dict in rest_client.list_records(
                "/rest/v1/VirDomainSnapshot", query
            )
        ]

        return snapshots

    @classmethod
    def filter_snapshots_by_params(
        cls,
        params: dict[
            Any, Any
        ],  # params must be a dict with keys: "vm_name", "serial", "label"
        rest_client: RestClient,
    ) -> List[TypedVMSnapshotToAnsible]:
        vm_snapshots = cls.get_snapshots_by_query({}, rest_client)
        if not params["vm_name"] and not params["serial"] and not params["label"]:
            return (
                vm_snapshots  # return all snapshots if none of the params are present
            )

        # else filter results by label, vm.name, vm.snapshotSerialNumber
        new_snaps = vm_snapshots[
            :
        ]  # for some unknown reason, using just "vm_snapshots" returns empty list: []
        if params["vm_name"]:
            new_snaps = [
                vm_snap
                for vm_snap in new_snaps
                if vm_snap["vm"]["name"] == params["vm_name"]  # type: ignore
            ]
        if params["serial"]:
            new_snaps = [
                vm_snap
                for vm_snap in new_snaps
                if vm_snap["vm"]["snapshot_serial_number"] == params["serial"]  # type: ignore
            ]
        if params["label"]:
            new_snaps = [
                vm_snap for vm_snap in new_snaps if vm_snap["label"] == params["label"]
            ]
        return new_snaps

    def send_create_request(self, rest_client: RestClient) -> TypedTaskTag:
        payload = self.to_hypercore()
        payload.pop("uuid")  # "uuid" is not allowed
        return rest_client.create_record("/rest/v1/VirDomainSnapshot", payload, False)

    @staticmethod
    def send_delete_request(
        rest_client: RestClient, snapshot_uuid: Optional[str]
    ) -> TypedTaskTag:
        if not snapshot_uuid:
            raise ScaleComputingError("Missing Snapshot UUID inside delete request.")
        return rest_client.delete_record(
            f"/rest/v1/VirDomainSnapshot/{snapshot_uuid}", False
        )

    @classmethod
    # Used to rename dict keys of a hypercore object that doesn't have an implemented class
    def hypercore_disk_to_ansible(
        cls, hypercore_dict: Optional[Dict[Any, Any]]
    ) -> Optional[Dict[Any, Any]]:
        if hypercore_dict is None:
            return None

        return dict(
            uuid=hypercore_dict["uuid"],
            disk_slot=hypercore_dict["slot"],
            type=hypercore_dict["type"].lower(),
            vm_uuid=hypercore_dict["virDomainUUID"],
            size=hypercore_dict["capacity"],
        )

    @classmethod
    def get_vm_disk_info_by_uuid(
        cls, disk_uuid: str, rest_client: RestClient
    ) -> Optional[Dict[Any, Any]]:
        record_dict = rest_client.get_record(
            endpoint="/rest/v1/VirDomainBlockDevice",
            query={"uuid": disk_uuid},
        )
        return cls.hypercore_disk_to_ansible(record_dict)

    @classmethod
    def get_vm_disk_info(
        cls, vm_uuid: str, slot: int, _type: str, rest_client: RestClient
    ) -> Optional[Dict[Any, Any]]:
        record_dict = rest_client.get_record(
            endpoint="/rest/v1/VirDomainBlockDevice",
            query={
                "virDomainUUID": vm_uuid,
                "slot": slot,
                "type": _type,
            },
        )
        return cls.hypercore_disk_to_ansible(record_dict)

    @classmethod
    def get_snapshot_disk(
        cls,
        vm_snapshot: TypedVMSnapshotToAnsible,
        slot: int,
        _type: str,
    ) -> Any:
        disks = copy(vm_snapshot["vm"]["disks"])  # type: ignore

        disks = [d for d in disks if d["disk_slot"] == slot]

        disks = [d for d in disks if d["type"] == _type]

        if len(disks) > 1:
            raise errors.ScaleComputingError(
                "There are too many device snapshots of the provided filter. There should be only one."
            )
        if len(disks) == 0:
            return None
        return disks[0]

    @classmethod
    # Get VM UUID of a VM which does not have this snapshot
    def get_external_vm_uuid(cls, vm_name: str, rest_client: RestClient) -> Any:
        vm_hypercore_dict = rest_client.get_record(
            endpoint="/rest/v1/VirDomain", query={"name": vm_name}
        )
        if vm_hypercore_dict is None:
            return None

        return vm_hypercore_dict["uuid"]
