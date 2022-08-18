# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.state import ReplicationState


class Replication(PayloadMapper):
    def __init__(self):
        self.vm_uuid = None
        self.vm_name = None
        self.replication_uuid = None
        self.state = None
        # TODO: rename after remote_cluster_info is implemented
        self.remote_cluster_connection_uuid = None

    @classmethod
    def handle_state(cls, enable):
        if enable:
            return "enabled"
        return "disabled"

    @classmethod
    def get(cls, query, rest_client):
        record = rest_client.list_records(
            endpoint="/rest/v1/VirDomainReplication/",
            query=query,
        )
        if not record:
            return []
        return [
            Replication.from_hypercore(hypercore_data=replication)
            for replication in record
        ]

    @classmethod
    def from_hypercore(cls, hypercore_data):
        obj = Replication()
        obj.replication_uuid = hypercore_data["uuid"]
        obj.vm_uuid = hypercore_data["sourceDomainUUID"]
        obj.state = Replication.handle_state(hypercore_data["enable"])
        # TODO: When remote_cluster_info is implemented, replace this with cluster name
        obj.remote_cluster_connection_uuid = hypercore_data["connectionUUID"]
        return obj

    @classmethod
    def from_ansible(cls, ansible_data, virtual_machine_obj):
        # TODO: Implement with vm_replication module
        obj = Replication()
        obj.vm_name = virtual_machine_obj.name
        obj.vm_uuid = virtual_machine_obj.uuid
        obj.state = ansible_data["state"]
        obj.remote_cluster_connection_uuid = ansible_data.get("remote_cluster", None)
        return obj

    def to_hypercore(self):
        # TODO: Implement with vm_replication module
        replication_dict = {
            "sourceDomainUUID": self.vm_uuid,
            "connectionUUID": self.remote_cluster_connection_uuid,
        }
        if (
            self.state == ReplicationState.enabled
            or self.state == ReplicationState.reenabled
        ):
            replication_dict["enable"] = True
        elif self.state == ReplicationState.disabled:
            replication_dict["enable"] = False
        return replication_dict

    def to_ansible(self, virtual_machine_obj):
        replication_info_dict = {
            "vm_name": virtual_machine_obj.name,
            # TODO: When remote_cluster_info is implemented, replace this with cluster name
            "remote_cluster": self.remote_cluster_connection_uuid,
            "state": self.state,
        }
        return replication_info_dict