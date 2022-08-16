# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper


class Replication(PayloadMapper):
    def __init__(self):
        self.vm_uuid = None
        self.vm_name = None
        self.replication_uuid = None
        self.state = None
        #TODO: rename after remote_cluster_info is implemented
        self.remote_cluster_connection_uuid = None

    @classmethod
    def handle_state(cls, enable):
        if enable:
            return "enabled"
        return "disabled"

    @classmethod
    def get(cls, rest_client, vm_uuid):
        endpoint = "/rest/v1/VirDomainReplication/"
        replication = rest_client.get_record(
            endpoint, query={"sourceDomainUUID": vm_uuid}, must_exist=False
        )
        return replication

    @classmethod
    def create_from_hypercore(cls, hypercore_data, virtual_machine_obj):
        obj = Replication()
        obj.replication_uuid = hypercore_data["uuid"]
        obj.vm_name = virtual_machine_obj.name
        obj.vm_uuid = virtual_machine_obj.uuid
        obj.state = Replication.handle_state(hypercore_data["enable"])
        # TODO: When remote_cluster_info is implemented, replace this with cluster name
        obj.remote_cluster_connection_uuid = hypercore_data["connectionUUID"]
        return obj

    @classmethod
    def create_from_ansible(cls, hypercore_data, virtual_machine_obj):
        # TODO: Implement with vm_replication module
        return

    def data_to_hypercore(self):
        # TODO: Implement with vm_replication module
        return

    def data_to_ansible(self):
        replication_info_dict = {
            "vm_name": self.vm_name,
            #TODO: When remote_cluster_info is implemented, replace this with cluster name
            "remote_cluster": self.remote_cluster_connection_uuid,
            "state": self.state,
        }
        return replication_info_dict
