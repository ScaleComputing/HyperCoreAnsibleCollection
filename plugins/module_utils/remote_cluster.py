# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper


class RemoteCluster(PayloadMapper):
    def __init__(
        self,
        name,
        connection_status,
        replication_ok,
        remote_node_ips,
        remote_node_uuids,
    ):
        self.name = name
        self.connection_status = connection_status
        self.replication_ok = replication_ok
        self.remote_node_ips = remote_node_ips
        self.remote_node_uuids = remote_node_uuids

    @classmethod
    def from_ansible(cls):
        pass

    @classmethod
    def from_hypercore(cls, hypercore_data):
        if not hypercore_data:
            return None
        return cls(
            name=hypercore_data["remoteClusterInfo"]["clusterName"],
            connection_status=hypercore_data["connectionStatus"],
            replication_ok=hypercore_data["replicationOK"],
            remote_node_ips=hypercore_data["remoteNodeIPs"],
            remote_node_uuids=hypercore_data["remoteNodeUUIDs"],
        )

    def to_hypercore(self):
        pass

    def to_ansible(self):
        return dict(
            name=self.name,
            connection_status=self.connection_status,
            replication_ok=self.replication_ok,
            remote_node_ips=self.remote_node_ips,
            remote_node_uuids=self.remote_node_uuids,
        )

    def __eq__(self, other):
        """
        One Node is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        return all(
            (
                self.name == other.name,
                self.connection_status == other.connection_status,
                self.replication_ok == other.replication_ok,
                self.remote_node_ips == other.remote_node_ips,
                self.remote_node_uuids == other.remote_node_uuids,
            )
        )

    @classmethod
    def get_cluster_name_from_replication_connection_uuid(
        cls, rest_client, connection_uuid
    ):
        hypercore_dict = rest_client.get_record(
            "/rest/v1/RemoteClusterConnection", {"uuid": connection_uuid}
        )
        if hypercore_dict is None:
            return None
        record = cls.from_hypercore(hypercore_data=hypercore_dict).to_ansible()
        return record["name"]
