# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from .rest_client import RestClient

from ..module_utils.utils import PayloadMapper, get_query

from ..module_utils.typed_classes import (
    TypedVMSnapshotToAnsible,
    TypedVMSnapshotFromAnsible,
)
from typing import List, Any, Dict, Optional


class VMSnapshot(PayloadMapper):
    def __init__(
        self,
        uuid: Optional[str] = None,
        domain_uuid: Optional[str] = None,
        timestamp: Optional[int] = None,
        label: Optional[str] = None,
        type: Optional[int] = None,
        automated_trigger_timestamp: Optional[int] = None,
        local_retain_until_timestamp: Optional[int] = None,
        remote_retain_until_timestamp: Optional[int] = None,
        block_count_diff_from_serial_number: Optional[int] = None,
        replication: Optional[bool] = None,
    ):
        self.uuid = uuid
        self.domain_uuid = domain_uuid
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
            uuid=ansible_data["uuid"],
            domain_uuid=ansible_data["domain_uuid"],
            label=ansible_data["label"],
            type=ansible_data["type"],
        )

    @classmethod
    def from_hypercore(cls, hypercore_data: Dict[Any, Any]) -> Optional[VMSnapshot]:
        if not hypercore_data:
            return None
        return cls(
            uuid=hypercore_data["uuid"],
            domain_uuid=hypercore_data["domainUUID"],
            timestamp=hypercore_data["timestamp"],
            label=hypercore_data["label"],
            type=hypercore_data["type"],
            automated_trigger_timestamp=hypercore_data["automatedTriggerTimestamp"],
            local_retain_until_timestamp=hypercore_data["localRetainUntilTimestamp"],
            remote_retain_until_timestamp=hypercore_data["remoteRetainUntilTimestamp"],
            replication=hypercore_data["replication"],
        )

    def to_hypercore(self) -> Dict[Any, Any]:
        return dict(
            uuid=self.domain_uuid,
            domain_uuid=self.domain_uuid,
            label=self.label,
            type=self.type,
        )

    def to_ansible(self) -> TypedVMSnapshotToAnsible:
        return dict(
            uuid=self.uuid,
            domain_uuid=self.domain_uuid,
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
                self.uuid == other.uuid,
                self.domain_uuid == other.domain_uuid,
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
    def get_by_uuid(
        cls,
        ansible_dict: Dict[Any, Any],
        rest_client: RestClient,
        must_exist: bool = False,
    ) -> Optional[VMSnapshot]:
        query = get_query(ansible_dict, "uuid", ansible_hypercore_map=dict(uuid="uuid"))
        hypercore_dict = rest_client.get_record(
            "/rest/v1/VirDomainSnapshot", query, must_exist=must_exist
        )
        vm_snapshot_from_hypercore = cls.from_hypercore(hypercore_dict)  # type: ignore
        return vm_snapshot_from_hypercore

    @classmethod
    def get_by_snapshots_label(
        cls,
        label: str,
        rest_client: RestClient,
    ) -> List[Optional[TypedVMSnapshotToAnsible]]:
        snapshots = [
            cls.from_hypercore(hypercore_data=hypercore_dict).to_ansible()  # type: ignore
            for hypercore_dict in rest_client.list_records(
                "/rest/v1/VirDomainSnapshot", {"label": label}
            )
        ]

        return snapshots
