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
        remote_node_uuids
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
    def from_hypercore(cls, remote_cluster_dict):
        if not remote_cluster_dict:  # In case for get_record, return None if no result is found
            return None
        return RemoteCluster(
            name=remote_cluster_dict["remoteClusterInfo"]["clusterName"],
            connection_status=remote_cluster_dict["connectionStatus"],
            replication_ok=remote_cluster_dict["replicationOK"],
            remote_node_ips=remote_cluster_dict["remoteNodeIPs"],
            remote_node_uuids=remote_cluster_dict["remoteNodeUUIDs"],
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
