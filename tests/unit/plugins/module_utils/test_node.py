from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.node import Node

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestNode:
    def test_node_from_hypercore_dict_not_empty(self):
        node = Node(
            node_uuid="51e6d073-7566-4273-9196-58720117bd7f",
            backplane_ip="10.0.0.1",
            lan_ip="10.0.0.2",
            peer_id=6,
        )

        hypercore_dict = dict(
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
            backplaneIP="10.0.0.1",
            lanIP="10.0.0.2",
            peerID=6,
        )

        node_from_hypercore = Node.from_hypercore(hypercore_dict)
        assert node == node_from_hypercore

    def test_node_from_hypercore_dict_empty(self):
        assert Node.from_hypercore([]) is None

    def test_node_to_ansible(self):
        node = Node(
            node_uuid="51e6d073-7566-4273-9196-58720117bd7f",
            backplane_ip="10.0.0.1",
            lan_ip="10.0.0.1",
            peer_id=1,
        )

        ansible_dict = dict(
            node_uuid="51e6d073-7566-4273-9196-58720117bd7f",
            backplane_ip="10.0.0.1",
            lan_ip="10.0.0.1",
            peer_id=1,
        )

        assert node.to_ansible() == ansible_dict

    def test_get_from_uuid(self, rest_client):
        node_uuid = "51e6d073-7566-4273-9196-58720117bd7f"
        rest_client.get_record.return_value = dict(
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
            backplaneIP="10.0.0.1",
            lanIP="10.0.0.1",
            peerID=1,
        )
        node_from_hypercore = Node.get_by_uuid(node_uuid, rest_client)

        assert node_from_hypercore == Node(
            node_uuid="51e6d073-7566-4273-9196-58720117bd7f",
            backplane_ip="10.0.0.1",
            lan_ip="10.0.0.1",
            peer_id=1,
        )

    def test_get_from_uuid_no_record(self, rest_client):
        node_uuid = "51e6d073-7566-4273-9196-58720117bd7f"
        rest_client.get_record.return_value = None
        node_from_hypercore = Node.get_by_uuid(node_uuid, rest_client)

        assert node_from_hypercore is None
