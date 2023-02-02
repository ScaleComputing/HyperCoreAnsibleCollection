# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils import errors
from ..module_utils.rest_client import RestClient
from ..module_utils.task_tag import TypedTaskTag
from typing import TypedDict, Union


# Use for type hinting.
class TypedRegistrationToAnsible(TypedDict):
    company_name: str
    contact: str
    phone: str
    email: str


class Registration(PayloadMapper):
    def __init__(
        self,
        uuid: str = "",
        company_name: str = "",
        contact: str = "",
        phone: str = "",
        email: str = "",
        cluster_id: str = "",
        cluster_data: str = "",
        cluster_data_hash: str = "",
        cluster_data_hash_accepted: str = "",
    ):
        self.uuid = uuid
        self.company_name = company_name
        self.contact = contact
        self.phone = phone
        self.email = email
        self.cluster_id = cluster_id
        self.cluster_data = cluster_data
        self.cluster_data_hash = cluster_data_hash
        self.cluster_data_hash_accepted = cluster_data_hash_accepted

    @classmethod
    def get(cls, rest_client: RestClient) -> Union[Registration, None]:
        result = rest_client.list_records("/rest/v1/Registration")
        if result:
            # One registration per cluster.
            return cls.from_hypercore(result[0])
        return None

    @classmethod
    def from_hypercore(cls, hypercore_data: dict) -> Registration:
        try:
            obj = cls()
            obj.uuid = hypercore_data["uuid"]
            obj.company_name = hypercore_data["companyName"]
            obj.contact = hypercore_data["contact"]
            obj.phone = hypercore_data["phone"]
            obj.email = hypercore_data["email"]
            obj.cluster_id = hypercore_data["clusterID"]
            obj.cluster_data = hypercore_data["clusterData"]
            obj.cluster_data_hash = hypercore_data["clusterDataHash"]
            obj.cluster_data_hash_accepted = hypercore_data["clusterDataHashAccepted"]
            return obj
        except KeyError as e:
            raise errors.MissingValueHypercore(e)

    @classmethod
    def from_ansible(cls, ansible_data: dict) -> Registration:
        obj = cls()
        obj.company_name = ansible_data.get("company_name", None)
        obj.contact = ansible_data.get("contact", None)
        obj.phone = ansible_data.get("phone", None)
        obj.email = ansible_data.get("email", None)
        return obj

    def to_hypercore(self) -> dict:
        hypercore_dict = dict()
        if self.company_name:
            hypercore_dict["companyName"] = self.company_name
        if self.contact:
            hypercore_dict["contact"] = self.contact
        if self.phone is not None:
            hypercore_dict["phone"] = self.phone
        if self.email:
            hypercore_dict["email"] = self.email
        return hypercore_dict

    def to_ansible(self) -> TypedRegistrationToAnsible:
        return dict(
            company_name=self.company_name,
            contact=self.contact,
            phone=self.phone,
            email=self.email,
        )

    def send_create_request(self, rest_client: RestClient) -> TypedTaskTag:
        payload = self.to_hypercore()
        return rest_client.create_record("/rest/v1/Registration", payload, False)

    def send_delete_request(self, rest_client: RestClient) -> TypedTaskTag:
        return rest_client.delete_record(
            "/rest/v1/Registration/registration_guid", False
        )

    def send_update_request(self, rest_client: RestClient) -> TypedTaskTag:
        payload = self.to_hypercore()
        return rest_client.update_record(
            "/rest/v1/Registration/registration_guid", payload, False
        )
