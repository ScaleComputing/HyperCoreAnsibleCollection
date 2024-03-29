# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.role import Role
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import TypedUserToAnsible
from typing import Optional


class User(PayloadMapper):
    def __init__(
        self,
        uuid: str,
        username: str,
        full_name: str,
        role_uuids: list[str],
        session_limit: int,
    ):
        self.uuid = uuid
        self.username = username
        self.full_name = full_name
        self.role_uuids = role_uuids
        self.session_limit = session_limit

    @classmethod
    def from_ansible(cls):
        pass

    @classmethod
    def from_hypercore(cls, hypercore_data: dict) -> Optional[User]:
        # In case for get_record, return None if no result is found
        if not hypercore_data:
            return None
        return cls(
            uuid=hypercore_data["uuid"],
            username=hypercore_data["username"],
            full_name=hypercore_data["fullName"],
            role_uuids=hypercore_data["roleUUIDs"],
            session_limit=hypercore_data["sessionLimit"],
        )

    def to_hypercore(self):
        pass

    def to_ansible(self, rest_client: RestClient) -> TypedUserToAnsible:
        return dict(
            uuid=self.uuid,
            username=self.username,
            full_name=self.full_name,
            roles=[
                Role.get_role_from_uuid(
                    role_uuid, rest_client, must_exist=False
                ).to_ansible()
                for role_uuid in self.role_uuids
            ],
            session_limit=self.session_limit,
        )

    def __eq__(self, other: object) -> bool:
        """
        One User is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        if not isinstance(other, User):
            return NotImplemented
        return all(
            (
                self.uuid == other.uuid,
                self.username == other.username,
                self.full_name == other.full_name,
                self.role_uuids == other.role_uuids,
                self.session_limit == other.session_limit,
            )
        )

    @classmethod
    def get_user_from_uuid(
        cls, user_uuid, rest_client: RestClient, must_exist: bool = False
    ) -> Optional[User]:
        hypercore_dict = rest_client.get_record(
            "/rest/v1/User/{0}".format(user_uuid), must_exist=must_exist
        )
        user = cls.from_hypercore(hypercore_dict)
        return user

    @classmethod
    def get_user_from_username(
        cls, username, rest_client: RestClient, must_exist: bool = False
    ) -> Optional[User]:
        hypercore_dict = rest_client.get_record(
            "/rest/v1/User", {"username": username}, must_exist=must_exist
        )
        user = cls.from_hypercore(hypercore_dict)
        return user

    def delete(self, rest_client: RestClient, check_mode: bool = False) -> None:
        rest_client.delete_record(f"/rest/v1/User/{self.uuid}", check_mode)
        # returned:
        # {
        #     "taskTag": "",
        #     "createdUUID": ""
        # }

    def update(
        self, rest_client: RestClient, payload, check_mode: bool = False
    ) -> None:
        rest_client.update_record(f"/rest/v1/User/{self.uuid}", payload, check_mode)
        # returned:
        # {
        #     "taskTag": "",
        #     "createdUUID": ""
        # }

    @classmethod
    def create(cls, rest_client: RestClient, payload, check_mode=False) -> User:
        task_tag = rest_client.create_record("/rest/v1/User", payload, check_mode)
        user = cls.get_user_from_uuid(
            task_tag["createdUUID"], rest_client, must_exist=True
        )
        return user  # type: ignore # user is never None
        # returned
        # {
        #   "taskTag": "",
        #   "createdUUID": "e022a3ca-ceb4-40c9-8ed0-7cd594640f12"
        # }
