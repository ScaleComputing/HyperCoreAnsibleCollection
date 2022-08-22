# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.type import NicType
from ..module_utils.utils import PayloadMapper
from ..module_utils.task_tag import TaskTag
from ..module_utils import errors


class Nic(PayloadMapper):
    def __init__(self):
        self.uuid = None
        self.vm_uuid = None
        self.type = None
        self.mac = None
        self.mac_new = None
        # Hypercore adds default value of vlan to 0, so we do the same.
        self.vlan = 0
        self.vlan_new = None
        self.connected = None
        self.ipv4Addresses = []

    def __eq__(self, other):
        if self.vlan_new is not None and not self.mac_new:
            return (
                self.vlan_new == other.vlan
                and self.type == other.type
                and self.vm_uuid == other.vm_uuid
            )
        elif other.vlan_new is not None and not other.mac_new:
            return (
                self.vlan == other.vlan_new
                and self.type == other.type
                and self.vm_uuid == other.vm_uuid
            )
        elif self.mac_new and self.vlan_new is None:
            return (
                self.vlan == other.vlan
                and self.type == other.type
                and self.vm_uuid == other.vm_uuid
                and self.mac_new == other.mac
            )
        elif other.mac_new and other.vlan_new is None:
            return (
                self.vlan == other.vlan
                and self.type == other.type
                and self.vm_uuid == other.vm_uuid
                and self.mac == other.mac_new
            )
        elif self.vlan_new is not None and self.mac_new:
            return (
                self.vlan_new == other.vlan
                and self.type == other.type
                and self.vm_uuid == other.vm_uuid
                and self.mac_new == other.mac
            )
        elif other.vlan_new is not None and other.mac_new:
            return (
                self.vlan == other.vlan_new
                and self.type == other.type
                and self.vm_uuid == other.vm_uuid
                and self.mac == other.mac_new
            )
        return (
            self.vlan == other.vlan
            and self.type == other.type
            and self.vm_uuid == other.vm_uuid
        )

    @classmethod
    def handle_nic_type(cls, nic_type):
        if nic_type:
            if nic_type.upper() == NicType.INTEL_E1000:
                actual_nic_type = nic_type.upper()  # INTEL_E1000
            elif nic_type.upper() == NicType.VIRTIO:
                actual_nic_type = nic_type.lower()  # virtio
            else:
                actual_nic_type = nic_type.upper()  # RTL8139
            return actual_nic_type
        return nic_type

    @classmethod
    def from_hypercore(cls, hypercore_data):
        # If exception is thrown, there has been a change in the API or a big problem on their side.
        try:
            obj = Nic()
            obj.uuid = hypercore_data["uuid"]
            obj.vm_uuid = hypercore_data["virDomainUUID"]
            obj.type = Nic.handle_nic_type(hypercore_data["type"])
            obj.mac = hypercore_data["macAddress"]
            obj.vlan = hypercore_data["vlan"]
            obj.connected = hypercore_data["connected"]
            obj.ipv4Addresses = hypercore_data["ipv4Addresses"]
            return obj
        except KeyError as e:
            raise errors.MissingValueHypercore(e)

    @classmethod
    def from_ansible(cls, ansible_data):
        obj = Nic()
        obj.vm_uuid = ansible_data.get("vm_uuid", None)
        obj.type = Nic.handle_nic_type(ansible_data.get("type", None))
        obj.mac = ansible_data.get("mac", None)
        obj.mac_new = ansible_data.get("mac_new", None)
        obj.vlan = ansible_data.get("vlan", 0)
        obj.vlan_new = ansible_data.get("vlan_new", None)
        return obj

    @classmethod
    def get_by_uuid(cls, rest_client, nic_uuid):
        return Nic.from_hypercore(
            rest_client.get_record(
                "/rest/v1/VirDomainNetDevice", query={"uuid": nic_uuid}, must_exist=True
            )
        )

    @classmethod
    def send_update_nic_request_to_hypercore(
        cls, rest_client, new_nic, existing_nic, before, after
    ):
        if new_nic is None or existing_nic is None:
            raise errors.MissingFunctionParameter(
                "new_nic or existing_nic - nic.py - update_nic_to_hypercore()"
            )
        before.append(existing_nic.to_ansible())
        data = new_nic.to_hypercore()
        response = rest_client.update_record(
            endpoint="/rest/v1/VirDomainNetDevice/" + existing_nic.uuid,
            payload=data,
            check_mode=False,
        )
        new_nic_obj = Nic.get_by_uuid(
            rest_client=rest_client, nic_uuid=existing_nic.uuid
        )
        after.append(new_nic_obj.to_ansible())
        TaskTag.wait_task(rest_client=rest_client, task=response)
        return True, before, after

    @classmethod
    def send_create_nic_request_to_hypercore(cls, rest_client, new_nic, before, after):
        if new_nic is None:
            raise errors.MissingFunctionParameter(
                "new_nic - nic.py - create_nic_to_hypercore()"
            )
        before.append(None)
        data = new_nic.to_hypercore()
        response = rest_client.create_record(
            endpoint="/rest/v1/VirDomainNetDevice", payload=data, check_mode=False
        )
        new_nic_obj = Nic.get_by_uuid(
            rest_client=rest_client, nic_uuid=response["createdUUID"]
        )
        after.append(new_nic_obj.to_ansible())
        TaskTag.wait_task(rest_client=rest_client, task=response)
        return True, before, after

    @classmethod
    def send_delete_nic_request_to_hypercore(
        cls, rest_client, nic_to_delete, before, after
    ):
        if nic_to_delete is None:
            raise errors.MissingFunctionParameter(
                "nic_to_delete - nic.py - delete_nic_to_hypercore()"
            )
        before.append(nic_to_delete.to_ansible())
        response = rest_client.delete_record(
            endpoint="/rest/v1/VirDomainNetDevice/" + nic_to_delete.uuid,
            check_mode=False,
        )
        after.append(None)
        TaskTag.wait_task(rest_client=rest_client, task=response)
        return True, before, after

    # Compares hc3 nic to ansible nic
    def is_update_needed(self, ansible_nic):
        return not (self == ansible_nic)

    def to_hypercore(self):
        nic_dict = {
            "vlan": self.vlan,
            "virDomainUUID": self.vm_uuid,
        }
        # TODO corner case: change vlan 0 -> 10, 10 -> 0. integration test
        if self.uuid:
            nic_dict["uuid"] = self.uuid
        if self.vlan_new is not None:
            nic_dict["vlan"] = self.vlan_new
        if self.type:
            nic_dict["type"] = self.type.upper()  # TODO enum
        if self.connected is not None:
            nic_dict["connected"] = self.connected
        if self.mac:  # if it's empty we don't send, it auto-generates
            nic_dict["macAddress"] = self.mac
        if self.mac_new:  # user wants to change mac address
            nic_dict["macAddress"] = self.mac_new
        return nic_dict

    def to_ansible(self):
        nic_info_dict = {
            "uuid": self.uuid,
            "vlan": self.vlan,
            "type": self.type,
            "mac": self.mac,
            "connected": self.connected,
            "ipv4_addresses": self.ipv4Addresses,
        }
        return nic_info_dict
