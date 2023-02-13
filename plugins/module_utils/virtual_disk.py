# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.typed_classes import (
    TypedVirtualDiskFromAnsible,
    TypedVirtualDiskToAnsible,
)
from typing import Union, Dict, List, Any

from .rest_client import RestClient
from ..module_utils.utils import PayloadMapper


class VirtualDisk(PayloadMapper):
    def __init__(
        self,
        name: Union[str, None] = None,
        uuid: Union[str, None] = None,
        block_size: Union[int, None] = None,
        size: Union[int, None] = None,
        # allocated_size: int = None,
        replication_factor: Union[int, None] = None,
    ):
        self.name = name
        self.uuid = uuid
        self.block_size = block_size
        self.size = size
        # self.allocated_size = allocated_size
        self.replication_factor = replication_factor

    @classmethod
    def from_ansible(cls, ansible_data: TypedVirtualDiskFromAnsible) -> VirtualDisk:
        return cls(
            name=ansible_data["name"],
        )

    @classmethod
    def from_hypercore(cls, hypercore_data: Dict[Any, Any]) -> VirtualDisk:
        return cls(
            name=hypercore_data["name"],
            uuid=hypercore_data["uuid"],
            block_size=hypercore_data["blockSize"],
            size=hypercore_data["capacityBytes"],
            # allocated_size=hypercore_data["totalAllocationBytes"],
            replication_factor=hypercore_data["replicationFactor"],
        )

    def to_hypercore(self) -> Dict[Any, Any]:
        raise NotImplementedError()
        # return dict(
        #     searchDomains=self.search_domains,
        #     serverIPs=self.server_ips,
        # )

    def to_ansible(self) -> TypedVirtualDiskToAnsible:
        return dict(
            name=self.name,
            uuid=self.uuid,
            block_size=self.block_size,
            size=self.size,
            # allocated_size=self.allocated_size,
            replication_factor=self.replication_factor,
        )

    # This method is here for testing purposes!
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VirtualDisk):
            return NotImplemented
        return all(
            (
                self.uuid == other.uuid,
                self.name == other.name,
                self.block_size == other.block_size,
                self.size == other.size,
                # self.allocated_size == other.allocated_size,
                self.replication_factor == other.replication_factor,
            )
        )

    # @classmethod
    # def get_by_uuid(cls, ansible_dict, rest_client, must_exist=False):
    #     query = get_query(ansible_dict, "uuid", ansible_hypercore_map=dict(uuid="uuid"))
    #     hypercore_dict = rest_client.get_record(
    #         "/rest/v1/VirtualDisk", query, must_exist=must_exist
    #     )
    #     virtual_disk = VirtualDisk.from_hypercore(hypercore_dict)
    #     return virtual_disk

    @classmethod
    def get_state(
        cls, rest_client: RestClient, query: Dict[Any, Any]
    ) -> List[TypedVirtualDiskToAnsible]:
        state = [
            VirtualDisk.from_hypercore(hypercore_data=hypercore_dict).to_ansible()
            for hypercore_dict in rest_client.list_records(
                "/rest/v1/VirtualDisk", query
            )
        ]
        return state
