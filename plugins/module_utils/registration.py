# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils import errors


class Registration(PayloadMapper):
    def __init__(self):
        self.uuid = None
        self.company_name = None
        self.contact = None
        self.phone = None
        self.email = None
        self.cluster_id = None
        self.cluster_data = None
        self.cluster_data_hash = None
        self.cluster_data_hash_accepted = None

    @classmethod
    def from_hypercore(cls, hypercore_data):
        try:
            obj = Registration()
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
    def from_ansible(cls, ansible_data):
        obj = Registration()
        obj.company_name = ansible_data.get("company_name", None)
        obj.contact = ansible_data.get("contact", None)
        obj.phone = ansible_data.get("phone", None)
        obj.email = ansible_data.get("email", None)
        return obj

    def to_hypercore(self):
        hypercore_dict = dict()
        if self.uuid:
            hypercore_dict["uuid"] = self.uuid
        if self.company_name:
            hypercore_dict["company_name"] = self.company_name
        if self.contact:
            hypercore_dict["contact"] = self.contact
        if self.phone is not None:
            hypercore_dict["phone"] = self.phone
        if self.email:
            hypercore_dict["email"] = self.email
        return hypercore_dict

    def to_ansible(self):
        return dict(
            uuid = self.uuid,
            company_name = self.company_name,
            contact = self.contact,
            phone = self.phone,
            email = self.email,
            cluster_id = self.cluster_id,
            cluster_data_hash = self.cluster_data_hash,
            cluster_data_hash_accepted = self.cluster_data_hash_accepted,
        )
