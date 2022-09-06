from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.remote_cluster import (
    RemoteCluster,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRemoteCluster:
    def test_remote_cluster_from_hypercore_dict_not_empty(self):
        node = RemoteCluster(
            name="PUB4",
            connection_status="ESTABLISHED",
            replication_ok=True,
            remote_node_ips=["10.5.11.11"],
            remote_node_uuids=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )

        hypercore_dict = dict(
            remoteClusterInfo={"clusterName": "PUB4"},
            connectionStatus="ESTABLISHED",
            replicationOK=True,
            remoteNodeIPs=["10.5.11.11"],
            remoteNodeUUIDs=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )

        remote_cluster_from_hypercore = RemoteCluster.from_hypercore(hypercore_dict)
        assert node == remote_cluster_from_hypercore

    def test_remote_cluster_from_hypercore_dict_empty(self):
        assert RemoteCluster.from_hypercore([]) is None

    def test_remote_cluster_to_ansible(self):
        remote_cluster = RemoteCluster(
            name="PUB4",
            connection_status="ESTABLISHED",
            replication_ok=True,
            remote_node_ips=["10.5.11.11"],
            remote_node_uuids=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )

        ansible_dict = dict(
            name="PUB4",
            connection_status="ESTABLISHED",
            replication_ok=True,
            remote_node_ips=["10.5.11.11"],
            remote_node_uuids=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )

        assert remote_cluster.to_ansible() == ansible_dict

    def test_equal_true(self):
        remote_cluster1 = RemoteCluster(
            name="PUB4",
            connection_status="ESTABLISHED",
            replication_ok=True,
            remote_node_ips=["10.5.11.11"],
            remote_node_uuids=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )
        remote_cluster2 = RemoteCluster(
            name="PUB4",
            connection_status="ESTABLISHED",
            replication_ok=True,
            remote_node_ips=["10.5.11.11"],
            remote_node_uuids=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )

        assert remote_cluster1 == remote_cluster2

    def test_equal_false(self):
        remote_cluster1 = RemoteCluster(
            name="PUB4",
            connection_status="ESTABLISHED",
            replication_ok=True,
            remote_node_ips=["10.5.11.11"],
            remote_node_uuids=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )
        remote_cluster2 = RemoteCluster(
            name="PUB3",
            connection_status="ESTABLISHED",
            replication_ok=True,
            remote_node_ips=["10.5.11.11"],
            remote_node_uuids=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )

        assert remote_cluster1 != remote_cluster2

    def test_get_cluster_name_from_replication_connection_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(
            remoteClusterInfo={"clusterName": "PUB4"},
            connectionStatus="ESTABLISHED",
            replicationOK=True,
            remoteNodeIPs=["10.5.11.11"],
            remoteNodeUUIDs=["895033ed-b863-4a42-8215-477a1a4ef812"],
        )

        remote_cluster_name = (
            RemoteCluster.get_cluster_name_from_replication_connection_uuid(
                rest_client, "891f482a-8f5f-4755-bea4-bbcc338f566f"
            )
        )

        assert remote_cluster_name == "PUB4"

    def test_get_cluster_name_from_replication_connection_uuid_record_missing(
        self, rest_client
    ):
        rest_client.get_record.return_value = None
        remote_cluster_name = (
            RemoteCluster.get_cluster_name_from_replication_connection_uuid(
                rest_client, "891f482a-8f5f-4755-bea4-bbcc338f566f"
            )
        )

        assert remote_cluster_name is None
