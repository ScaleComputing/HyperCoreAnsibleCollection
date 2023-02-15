# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import TypedClusterToAnsible
from typing import Any


class Cluster(PayloadMapper):
    def __init__(self, uuid: str, name: str):
        self.uuid = uuid
        self.name = name

    @classmethod
    def from_ansible(cls, ansible_data: dict[Any, Any]) -> None:
        pass

    @classmethod
    def from_hypercore(cls, hypercore_data: dict[Any, Any]) -> Cluster:
        return cls(
            uuid=hypercore_data["uuid"],
            name=hypercore_data["clusterName"],
        )

    def to_hypercore(self) -> None:
        pass

    def to_ansible(self) -> TypedClusterToAnsible:
        return dict(
            uuid=self.uuid,
            name=self.name,
        )

    def __eq__(self, other: object) -> bool:
        """
        One Cluster is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        if not isinstance(other, Cluster):
            return NotImplemented
        return all(
            (
                self.uuid == other.uuid,
                self.name == other.name,
            )
        )

    @classmethod
    def get(cls, rest_client: RestClient, must_exist: bool = True) -> Cluster:
        hypercore_dict = rest_client.get_record(
            "/rest/v1/Cluster", must_exist=must_exist
        )
        cluster = cls.from_hypercore(hypercore_dict)  # type: ignore # cluster never None
        return cluster

    def update_name(
        self, rest_client: RestClient, name_new: str, check_mode: bool = False
    ) -> None:
        rest_client.update_record(
            f"/rest/v1/Cluster/{self.uuid}", dict(clusterName=name_new), check_mode
        )
        # TODO wait on taskTag
        # returned:
        # {
        #     "taskTag": "",
        #     "createdUUID": ""
        # }
