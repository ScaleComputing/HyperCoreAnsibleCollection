# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import remote_cluster_info

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRun:
    def test_run_records_present(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="PUB4",
            ),
        )

        rest_client.list_records.return_value = [
            dict(
                remoteClusterInfo={"clusterName": "PUB4"},
                connectionStatus="ESTABLISHED",
                replicationOK=True,
                remoteNodeIPs=["10.5.11.11"],
                remoteNodeUUIDs=["895033ed-b863-4a42-8215-477a1a4ef812"],
            )
        ]

        result = remote_cluster_info.run(module, rest_client)
        assert result == [
            {
                "name": "PUB4",
                "connection_status": "ESTABLISHED",
                "replication_ok": True,
                "remote_node_ips": ["10.5.11.11"],
                "remote_node_uuids": ["895033ed-b863-4a42-8215-477a1a4ef812"],
            }
        ]

    def test_run_records_present_without_selected_cluster(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="PUB3",
            ),
        )

        rest_client.list_records.return_value = [
            dict(
                remoteClusterInfo={"clusterName": "PUB4"},
                connectionStatus="ESTABLISHED",
                replicationOK=True,
                remoteNodeIPs=["10.5.11.11"],
                remoteNodeUUIDs=["895033ed-b863-4a42-8215-477a1a4ef812"],
            )
        ]

        result = remote_cluster_info.run(module, rest_client)
        assert result == []

    def test_run_records_present_without_query(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name=None,
            ),
        )

        rest_client.list_records.return_value = [
            dict(
                remoteClusterInfo={"clusterName": "PUB4"},
                connectionStatus="ESTABLISHED",
                replicationOK=True,
                remoteNodeIPs=["10.5.11.11"],
                remoteNodeUUIDs=["895033ed-b863-4a42-8215-477a1a4ef812"],
            )
        ]

        result = remote_cluster_info.run(module, rest_client)
        assert result == [
            {
                "name": "PUB4",
                "connection_status": "ESTABLISHED",
                "replication_ok": True,
                "remote_node_ips": ["10.5.11.11"],
                "remote_node_uuids": ["895033ed-b863-4a42-8215-477a1a4ef812"],
            }
        ]

    def test_run_records_absent(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="PUB4",
            ),
        )

        rest_client.list_records.return_value = []

        result = remote_cluster_info.run(module, rest_client)
        assert result == []
