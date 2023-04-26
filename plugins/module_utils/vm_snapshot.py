# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from .rest_client import RestClient

from ..module_utils.utils import PayloadMapper

from ..module_utils.typed_classes import (
    TypedVMSnapshotToAnsible,
    TypedVMSnapshotFromAnsible,
)
from typing import List, Any, Dict, Optional


class VMSnapshot(PayloadMapper):
    def __init__(
        self,
        snapshot_uuid: Optional[str] = None,
        vm: Optional[Dict[Any, Any]] = None,
        timestamp: Optional[int] = None,
        label: Optional[str] = None,
        type: Optional[str] = None,
        automated_trigger_timestamp: Optional[int] = None,
        local_retain_until_timestamp: Optional[int] = None,
        remote_retain_until_timestamp: Optional[int] = None,
        block_count_diff_from_serial_number: Optional[int] = None,
        replication: Optional[bool] = True,
    ):
        self.snapshot_uuid = snapshot_uuid
        self.vm = vm if vm is not None else {}
        self.timestamp = timestamp
        self.label = label
        self.type = type
        self.automated_trigger_timestamp = automated_trigger_timestamp
        self.local_retain_until_timestamp = local_retain_until_timestamp
        self.remote_retain_until_timestamp = remote_retain_until_timestamp
        self.block_count_diff_from_serial_number = block_count_diff_from_serial_number
        self.replication = replication

    @classmethod
    def from_ansible(cls, ansible_data: TypedVMSnapshotFromAnsible) -> VMSnapshot:
        return VMSnapshot(
            snapshot_uuid=ansible_data["snapshot_uuid"],
            vm=ansible_data["vm"],
            label=ansible_data["label"],
            type=ansible_data["type"],
        )

    @classmethod
    def from_hypercore(cls, hypercore_data: Dict[Any, Any]) -> Optional[VMSnapshot]:
        if not hypercore_data:
            return None
        return cls(
            snapshot_uuid=hypercore_data["uuid"],
            vm={
                "name": hypercore_data["domain"]["name"],
                "uuid": hypercore_data["domainUUID"],
                "snapshot_serial_number": hypercore_data["domain"][
                    "snapshotSerialNumber"
                ],
            },
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
        return dict(
            snapshot_uuid=self.snapshot_uuid,
            vm=self.vm,
            label=self.label,
            type=self.type,
        )

    def to_ansible(self) -> TypedVMSnapshotToAnsible:
        return dict(
            snapshot_uuid=self.snapshot_uuid,
            vm=self.vm,
            timestamp=self.timestamp,
            label=self.label,
            type=self.type,
            automated_trigger_timestamp=self.automated_trigger_timestamp,
            local_retain_until_timestamp=self.local_retain_until_timestamp,
            remote_retain_until_timestamp=self.remote_retain_until_timestamp,
            block_count_diff_from_serial_number=self.block_count_diff_from_serial_number,
            replication=self.replication,
        )

    # This method is here for testing purposes!
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VMSnapshot):
            return NotImplemented
        return all(
            (
                self.snapshot_uuid == other.snapshot_uuid,
                self.vm == other.vm,
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
    def get_snapshots_by_query(  # will leave as is for now
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
            new_snaps = [vm_snap for vm_snap in new_snaps if vm_snap["vm"]["name"] == params["vm_name"]]  # type: ignore
        if params["serial"]:
            new_snaps = [vm_snap for vm_snap in new_snaps if vm_snap["vm"]["snapshot_serial_number"] == params["serial"]]  # type: ignore
        if params["label"]:
            new_snaps = [vm_snap for vm_snap in new_snaps if vm_snap["label"] == params["label"]]

        return new_snaps
