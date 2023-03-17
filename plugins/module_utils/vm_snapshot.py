# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from .rest_client import RestClient

from ..module_utils.utils import PayloadMapper, get_query, filter_results

from ..module_utils.typed_classes import (
    TypedVMSnapshotToAnsible,
    TypedVMSnapshotFromAnsible,
)
from typing import List, Any, Dict, Optional


class VMSnapshot(PayloadMapper):
    def __init__(
        self,
        vm_uuid: Optional[str] = None,
        domain_uuid: Optional[str] = None,
        domain: Optional[dict[Any, Any]] = None,
        timestamp: Optional[int] = None,
        label: Optional[str] = None,
        type: Optional[int] = None,
        automated_trigger_timestamp: Optional[int] = None,
        local_retain_until_timestamp: Optional[int] = None,
        remote_retain_until_timestamp: Optional[int] = None,
        block_count_diff_from_serial_number: Optional[int] = None,
        replication: Optional[bool] = True,
    ):
        self.vm_uuid = vm_uuid
        self.domain_uuid = domain_uuid
        self.domain = {} if domain is None else domain
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
            vm_uuid=ansible_data["vm_uuid"],
            domain_uuid=ansible_data["domain_uuid"],
            domain=ansible_data["domain"],
            label=ansible_data["label"],
            type=ansible_data["type"],
        )

    @classmethod
    def from_hypercore(cls, hypercore_data: Dict[Any, Any]) -> Optional[VMSnapshot]:
        if not hypercore_data:
            return None
        return cls(
            vm_uuid=hypercore_data["uuid"],
            domain_uuid=hypercore_data["domainUUID"],
            domain=hypercore_data["domain"],
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
            vm_uuid=self.vm_uuid,
            domain_uuid=self.domain_uuid,
            domain=self.domain,
            label=self.label,
            type=self.type,
        )

    def to_ansible(self) -> TypedVMSnapshotToAnsible:
        return dict(
            vm_uuid=self.vm_uuid,
            domain_uuid=self.domain_uuid,
            domain=self.domain,
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
                self.vm_uuid == other.vm_uuid,
                self.domain_uuid == other.domain_uuid,
                self.domain == other.domain,
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
        query: dict,
        rest_client: RestClient,
    ) -> List[Optional[TypedVMSnapshotToAnsible]]:
        snapshots = [
            cls.from_hypercore(hypercore_data=hypercore_dict).to_ansible()  # type: ignore
            for hypercore_dict in rest_client.list_records(
                "/rest/v1/VirDomainSnapshot", query
            )
        ]

        return snapshots

    @classmethod
    def get_by_snapshot_label(
        cls, label: str, rest_client: RestClient
    ) -> List[Optional[TypedVMSnapshotToAnsible]]:
        return cls.get_snapshots_by_query({"label": label}, rest_client)

    @classmethod
    def filter_by_vm_name_serial_label(
        cls,
        vm_snapshots: List[Optional[TypedVMSnapshotToAnsible]],
        params: dict[
            Any, Any
        ],  # params must be a dict with keys: "vm_name", "serial", "label"
        query: dict[
            Any, Any
        ],  # a dict with or without keys: "domain.name", "domain.snapshotSerialNumber", "label"
    ) -> List[Optional[TypedVMSnapshotToAnsible]]:
        return [
            vm_snapshot
            for vm_snapshot in vm_snapshots
            if (
                params["vm_name"]
                and vm_snapshot["domain"]["name"] == query["domain.name"]
            )
            or (
                params["serial"]
                and vm_snapshot["domain"]["snapshotSerialNumber"]
                == query["domain.snapshotSerialNumber"]
            )
            or (params["label"] and vm_snapshot["label"] == query["label"])
        ]

    # ===== Helper methods ======
    # will leave this method for now
    @classmethod
    def flatten_json_dict(cls, json_dict: dict[Any, Any]) -> Dict[Any, Any]:
        res = {}

        def flatten(json_obj: Any, name: str = ""):
            if type(json_obj) is dict:
                for el in json_obj:
                    flatten(json_obj[el], name + el + ".")
            elif type(json_obj) is list:
                i = 0
                for el in json_obj:
                    flatten(el, name + str(i) + ".")
                    i += 1
            else:
                res[name[:-1]] = json_obj

        flatten(json_dict)
        return res
