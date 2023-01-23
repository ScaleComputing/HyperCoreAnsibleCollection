# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.role import Role
from ..module_utils.rest_client import RestClient


class User(PayloadMapper):
    def __init__(self, uuid, username, fullname, role_uuids, session_limit):
        self.uuid = uuid
        self.username = username
        self.fullname = fullname
        self.role_uuids = role_uuids
        self.session_limit = session_limit

    @classmethod
    def from_ansible(cls):
        pass

    @classmethod
    def from_hypercore(cls, user_dict):
        if not user_dict:  # In case for get_record, return None if no result is found
            return None
        return cls(
            uuid=user_dict["uuid"],
            username=user_dict["username"],
            fullname=user_dict["fullName"],
            role_uuids=user_dict["roleUUIDs"],
            session_limit=user_dict["sessionLimit"],
        )

    def to_hypercore(self):
        pass

    def to_ansible(self, rest_client: RestClient):
        return dict(
            uuid=self.uuid,
            username=self.username,
            fullname=self.fullname,
            roles=[
                Role.get_role_from_uuid(
                    role_uuid, rest_client, must_exist=False
                ).to_ansible()
                for role_uuid in self.role_uuids
            ],
            session_limit=self.session_limit,
        )

    def __eq__(self, other):
        """
        One User is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        return all(
            (
                self.uuid == other.uuid,
                self.username == other.username,
                self.fullname == other.fullname,
                self.role_uuids == other.role_uuids,
                self.session_limit == other.session_limit,
            )
        )

    @classmethod
    def get_user(cls, query, rest_client: RestClient, must_exist=False):
        hypercore_dict = rest_client.get_record(
            "/rest/v1/User", query, must_exist=must_exist
        )
        user = cls.from_hypercore(hypercore_dict)
        return user
