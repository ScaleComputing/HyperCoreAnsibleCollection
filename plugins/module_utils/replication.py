# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.state import ReplicationState
from ..module_utils.remote_cluster import RemoteCluster
from ..module_utils.vm import VM
from ..module_utils import errors


class Replication(PayloadMapper):
    def __init__(self):
        self.vm_uuid = None
        self.vm_name = None
        self.replication_uuid = None
        self.state = None
        self.remote_cluster = None
        self.connection_uuid = None

    @classmethod
    def _replication(cls, rest_client, replication_dict):
        # Adds remote_cluster name and vm_name to the replication dict
        virtual_machine = VM.get_or_fail(
            query={"uuid": replication_dict["sourceDomainUUID"]},
            rest_client=rest_client,
        )[0]
        replication_dict[
            "remote_cluster"
        ] = RemoteCluster.get_cluster_name_from_replication_connection_uuid(
            rest_client, replication_dict["connectionUUID"]
        )
        replication_dict["vm_name"] = virtual_machine.name
        return replication_dict

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
            cls.from_hypercore(
                hypercore_data=cls._replication(rest_client, replication)
            )
            for replication in record
        ]

    @classmethod
    def from_hypercore(cls, hypercore_data):
        try:
            obj = cls()
            obj.replication_uuid = hypercore_data["uuid"]
            obj.vm_uuid = hypercore_data["sourceDomainUUID"]
            obj.vm_name = hypercore_data["vm_name"]
            obj.state = cls.handle_state(hypercore_data["enable"])
            obj.remote_cluster = hypercore_data["remote_cluster"]
            obj.connection_uuid = hypercore_data["connectionUUID"]
            return obj
        except KeyError as e:
            raise errors.MissingValueHypercore(e)

    @classmethod
    def from_ansible(cls, ansible_data, virtual_machine_obj, cluster_connection):
        obj = cls()
        obj.vm_name = virtual_machine_obj.name
        obj.vm_uuid = virtual_machine_obj.uuid
        obj.state = ansible_data["state"]
        obj.connection_uuid = cluster_connection["uuid"]
        obj.remote_cluster = ansible_data.get("remote_cluster", None)
        return obj

    @classmethod
    def find_available_cluster_connection_or_fail(cls, rest_client, ansible_dict):
        # Find the right cluster connection or fail!
        records = rest_client.list_records(
            endpoint="/rest/v1/RemoteClusterConnection",
            query=None,
        )
        if not records:
            raise errors.ClusterConnectionNotFound(
                "replication.py - find_available_cluster_connection_or_fail()"
            )
        if (
            "remote_cluster" in ansible_dict
            and ansible_dict["remote_cluster"] is not None
        ):
            # Try to find the correct cluster connection
            for cluster_connection in records:
                if (
                    cluster_connection["remoteClusterInfo"]["clusterName"].upper()
                    == ansible_dict["remote_cluster"].upper()
                ):
                    return cluster_connection
        raise errors.ScaleComputingError(
            f"Cluster connection to remote cluster {ansible_dict['remote_cluster']} does not exist, unable to create replication."
        )

    def to_hypercore(self):
        replication_dict = {
            "sourceDomainUUID": self.vm_uuid,
            "connectionUUID": self.connection_uuid,
        }
        if (
            self.state == ReplicationState.enabled
            or self.state == ReplicationState.reenabled
        ):
            replication_dict["enable"] = True
        elif self.state == ReplicationState.disabled:
            replication_dict["enable"] = False
        return replication_dict

    def to_ansible(self):
        replication_info_dict = {
            "vm_name": self.vm_name,
            "remote_cluster": self.remote_cluster,
            "state": self.state,
        }
        return replication_info_dict
