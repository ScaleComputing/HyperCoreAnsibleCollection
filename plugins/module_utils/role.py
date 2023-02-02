# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.rest_client import RestClient


class Role(PayloadMapper):
    def __init__(self, uuid, name):
        self.uuid = uuid
        self.name = name

    @classmethod
    def from_ansible(cls):
        pass

    @classmethod
    def from_hypercore(cls, hypercore_data):
        if not hypercore_data:
            # In case for get_record, return None if no result is found
            return None
        return cls(
            uuid=hypercore_data["uuid"],
            name=hypercore_data["name"],
        )

    def to_hypercore(self):
        pass

    def to_ansible(self):
        return dict(
            uuid=self.uuid,
            name=self.name,
        )

    def __eq__(self, other):
        """
        One User is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        return all(
            (
                self.uuid == other.uuid,
                self.name == other.name,
            )
        )

    @classmethod
    def get_role_from_uuid(cls, role_uuid, rest_client: RestClient, must_exist=False):
        hypercore_dict = rest_client.get_record(
            "/rest/v1/Role/{0}".format(role_uuid), must_exist=must_exist
        )
        role = cls.from_hypercore(hypercore_dict)
        return role

    @classmethod
    def get_role_from_name(cls, role_name, rest_client: RestClient, must_exist=False):
        hypercore_dict = rest_client.get_record(
            "/rest/v1/Role", {"name": role_name}, must_exist=must_exist
        )
        role = cls.from_hypercore(hypercore_dict)
        return role
