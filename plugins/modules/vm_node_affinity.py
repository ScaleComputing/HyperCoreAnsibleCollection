#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: vm

author:
  - Polona Mihalič (@PolonaM)
short_description: Update virtual machine's node affinity
description:
  - Module updates selected virtual machine's node affinity. 
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  vm_name:
    description:
      - Virtual machine name
      - Used to identify selected virtual machine by name
    type: str
    required: True
  strict_affinity:
    description:
      - Enable or disable strict enforcement of affinity strategy. The VirDomain will only run on preferred or backup node.
    type: bool
    required: True
  preferred_node:
    description:
      - Unique identifier of preferred node to run the VirDomain
    type: str
    required: True
  backup_node:
    description:
      - Unique identifier of backup node in the event that preferredNode is unavailable
    type: str
"""

EXAMPLES = r"""
- name: List all cluster nodes
  scale_computing.hypercore.node_info:
  register: nodes

  # results:
  # - node_uuid: "..."
  #   backplane_ip: "10.0.0.1"
  #   lan_ip: "10.0.0.1"
  #   peer_id: 1

- name: Set VM node affinity by node uuid
  scale_computing.hypercore.vm_node_affinity:
    vm_name: demo-vm
    strict_affinity: true
    prefferred_node:
      node_uuid: "{{ nodes.results[0].node_uuid }}"
    backup_node:
      node_uuid: "{{ nodes.results[1].node_uuid }}"

- name: Set VM node affinity by backplane IP or lan IP # One or another should be enough (backplane_ip or lan_ip). But task will return FAIL in case, that node can not be uniquely identifieed. In case that both are set, logical AND operation will be used.
  scale_computing.hypercore.vm_node_affinity:
    vm_name: demo-vm
    strict_affinity: true
    prefferred_node:
      backplane_ip: "10.0.0.1"
      lan_ip: "10.0.0.1"
      peer_id: 1
    backup_node:
      backplane_ip: "10.0.0.2"
      lan_ip: "10.0.0.2"
      peer_id: 2
"""

RETURN = r"""
vm:
  description:
    - A single VM record.
  returned: success
  type: dict  #?
  sample:
    vm_name: "vm-name"
    uuid: "1234-0001"
    state: "running"


# {
#   "taskTag": "7072",
#   "createdUUID": ""
# }
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.utils import get_query


def get_node_uuid(module, rest_client, vm_node_uuid):
    preferred_node_uuid = ""
    backup_node_uuid = ""
    if "node_uuid" in module.params["preferred_node"]:
        preferred_node_uuid = module.params["preferred_node"]["node_uuid"]
        if module.params["backup_node"] is not None:  # if backup_node is provided
            backup_node_uuid = module.params["backup_node"]["node_uuid"]
    else:
        query = get_query(
            module.params["preferred_node"],
            "backplane_ip",
            "lan_ip",
            ansible_hypercore_map=dict(backplane_ip="backplaneIP", lan_ip="lanIP"),
        )
        hypercore_dict = rest_client.get_record("/rest/v1/Node", query)
        if hypercore_dict is not None:
            preferred_node_uuid = hypercore_dict["uuid"]
        if module.params["backup_node"] is not None:  # if backup_node is provided
            query = get_query(
                module.params["backup_node"],
                "backplane_ip",
                "lan_ip",
                ansible_hypercore_map=dict(backplane_ip="backplaneIP", lan_ip="lanIP"),
            )
            hypercore_dict = rest_client.get_record("/rest/v1/Node", query)
            if hypercore_dict is not None:
                backup_node_uuid = hypercore_dict["uuid"]

    if (
        module.params["strict_affinity"] is True
        and preferred_node_uuid == ""
        and backup_node_uuid == ""
    ):
        if vm_node_uuid == "":
            strict_affinity = False
        preferred_node_uuid = vm_node_uuid
        strict_affinity = module.params["strict_affinity"]

    return strict_affinity, preferred_node_uuid, backup_node_uuid


def run(module, rest_client):
    # get vm's uuid from vm_name
    vm = VM.get_by_name(module.params, rest_client)
    endpoint = "{0}/{1}".format("/rest/v1/VirDomain", vm.uuid)
    strict_affinity, preferred_node_uuid, backup_node_uuid = get_node_uuid(
        module, rest_client, vm.node_uuid
    )
    payload = {
        "affinityStrategy": {
            "strictAffinity": strict_affinity,
            "preferredNodeUUID": preferred_node_uuid,
            "backupNodeUUID": backup_node_uuid,
        }
    }
    result = rest_client.update_record(endpoint, payload, module.check_mode)
    changed = True

    return changed, result


def main():
    module = AnsibleModule(
        supports_check_mode=True,  # False ATM
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            strict_affinity=dict(
                type="bool",
                required=True,
            ),
            preferred_node=dict(
                type="dict",
                required=True,
            ),
            backup_node=dict(
                type="dict",
            ),
        ),
    )
    # For valid/invalid combinations of strictAffinity/preferredNodeUUID/backupNodeUUID
    # In first iteration we will allow everything.
    # User will be able to set say strictaffinity=True even if backupNode is not set.
    # Trying to be smart (prevent obvios errors) can be delayed for now.
    # ATM only "strictAffinity=True and (preferredNodeUUID or backupNodeUUID not given)" case is something that should not happen.
    # But we need to write complete matrix for all before/after states if want to really check this.

    # If someone sets "Strict Affinity" and doesn't specify to which node the affinity should be set,
    # the affinity should be set automatically to the node that the VM is running on, or the next node on which the VM gets started.

    # Another corner case for "Strict Affinity" and doesn't specify to which node the affinity should be set,
    # the affinity should be set automatically to the node that the VM is running on -
    # if VM is not running yet (maybe was just created, and never run before) -
    # then Ansible really should not set strictaffinity=True . We need to be careful here.

    try:
        client = Client(
            host=module.params["cluster_instance"]["host"],
            username=module.params["cluster_instance"]["username"],
            password=module.params["cluster_instance"]["password"],
        )
        rest_client = RestClient(client)
        changed, result = run(module, rest_client)
        module.exit_json(changed=changed, result=result)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
