# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper


class Node(PayloadMapper):
    def __init__(self, node_uuid, backplane_ip, lan_ip, peer_id):
        self.node_uuid = node_uuid
        self.backplane_ip = backplane_ip
        self.lan_ip = lan_ip
        self.peer_id = peer_id

    @classmethod
    def from_ansible(cls):
        pass

    @classmethod
    def from_hypercore(cls, hypercore_data):
        if not hypercore_data:
            # In case for get_record, return None if no result is found
            return None
        return cls(
            node_uuid=hypercore_data["uuid"],
            backplane_ip=hypercore_data["backplaneIP"],
            lan_ip=hypercore_data["lanIP"],
            peer_id=hypercore_data["peerID"],
        )

    def to_hypercore(self):
        pass

    def to_ansible(self):
        return dict(
            node_uuid=self.node_uuid,
            backplane_ip=self.backplane_ip,
            lan_ip=self.lan_ip,
            peer_id=self.peer_id,
        )

    def __eq__(self, other):
        """
        One Node is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        return all(
            (
                self.node_uuid == other.node_uuid,
                self.backplane_ip == other.backplane_ip,
                self.lan_ip == other.lan_ip,
                self.peer_id == other.peer_id,
            )
        )

    @classmethod
    def get_node(cls, query, rest_client, must_exist=False):
        hypercore_dict = rest_client.get_record(
            "/rest/v1/Node", query, must_exist=must_exist
        )
        node_from_hypercore = cls.from_hypercore(hypercore_dict)
        return node_from_hypercore
