# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import TypedRoleToAnsible

from typing import Union, Any


class Role(PayloadMapper):
    def __init__(self, uuid: str, name: str):
        self.uuid = uuid
        self.name = name

    @classmethod
    def from_ansible(cls, ansible_data: Any) -> None:
        pass

    @classmethod
    def from_hypercore(
        cls, hypercore_data: Union[dict[Any, Any], None]
    ) -> Union[Role, None]:
        if not hypercore_data:
            # In case for get_record, return None if no result is found
            return None
        return cls(
            uuid=hypercore_data["uuid"],
            name=hypercore_data["name"],
        )

    def to_hypercore(self) -> None:
        pass

    def to_ansible(self) -> TypedRoleToAnsible:
        return dict(
            uuid=self.uuid,
            name=self.name,
        )

    def __eq__(self, other: object) -> bool:
        """
        One User is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        if not isinstance(other, Role):
            return NotImplemented
        return all(
            (
                self.uuid == other.uuid,
                self.name == other.name,
            )
        )

    @classmethod
    def get_role_from_uuid(
        cls, role_uuid: str, rest_client: RestClient, must_exist: bool = False
    ) -> Union[Role, None]:
        hypercore_dict = rest_client.get_record(
            "/rest/v1/Role/{0}".format(role_uuid), must_exist=must_exist
        )
        role = cls.from_hypercore(hypercore_dict)
        return role

    @classmethod
    def get_role_from_name(
        cls, role_name: str, rest_client: RestClient, must_exist: bool = False
    ) -> Union[Role, None]:
        hypercore_dict = rest_client.get_record(
            "/rest/v1/Role", {"name": role_name}, must_exist=must_exist
        )
        role = cls.from_hypercore(hypercore_dict)
        return role
