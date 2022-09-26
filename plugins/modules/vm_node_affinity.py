#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: vm_node_affinity

author:
  - Polona Mihalič (@PolonaM)
short_description: Update virtual machine's node affinity
description:
  - Module updates selected virtual machine node affinity.
    I(preferred_node) or I(backup_node) can be configured for each VM.
    The term I(node) later in this text means either I(preferred_node) or I(backup_node).
  - The I(node) can be selected by one or more parameters - I(node_uuid), I(backplane_ip), I(lan_ip) and/or I(peer_id).
    If I(node) is selected by multiple parameters, then all parameters must match,
    e.g. module internally performs logical C(AND) when searching for matching I(node) UUID.
  - If I(strict_affinity) is set to C(true), VM will only run on I(preferred_node) or I(backup_node).
  - If I(node) is not set, the old value of the I(node.node_uuid) will be kept.
  - If I(node.node_uuid) is set to empty string, the existing value of the I(node.node_uuid) will be deleted.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
seealso:
  - module: scale_computing.hypercore.node_info
options:
  strict_affinity:
    description:
      - Enable or disable strict enforcement of affinity strategy.
      - If C(preferred_node) and C(backup_node) are not set (in task or in VM) and C(strict_affinity) is set to True, the task will FAIL.
    type: bool
    required: True
  preferred_node:
    description:
      - Preferred node to run the VM
      - Can be set by C(node_uuid), C(backplane_ip), C(lan_ip) or C(peer_id)
      - One of the options should be enough. In case that all are set, logical AND operation is used.
        Task will FAIL in case that node can not be uniquely identified.
    type: dict
    suboptions:
      node_uuid:
        description: Unique identifier of preferred node
        type: str
      backplane_ip:
        description: Backplane IP of the preferred node
        type: str
      lan_ip:
        description: Lan IP of the preferred node
        type: str
      peer_id:
        description: Peer ID of the preffered node
        type: int
  backup_node:
    description:
      - Backup node in the event that preferred_node is unavailable
      - Can be set by C(node_uuid), C(backplane_ip), C(lan_ip) or C(peer_id)
      - One of the options should be enough. In case that all are set, logical AND operation is used.
        Task will FAIL in case that node can not be uniquely identified.
    type: dict
    suboptions:
      node_uuid:
        description: Unique identifier of backup node
        type: str
      backplane_ip:
        description: Backplane IP of the backup node
        type: str
      lan_ip:
        description: Lan IP of the backup node
        type: str
      peer_id:
        description: Peer ID of the backup node
        type: int
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Set VM node affinity by node uuid
  scale_computing.hypercore.vm_node_affinity:
    vm_name: demo-vm
    strict_affinity: true
    preferred_node:
      node_uuid: "412a3e85-8c21-4138-a36e-789eae3548a3"
    backup_node:
      node_uuid: "3dd52913-4e60-46fa-8ac6-07ba0b2155d2"

- name: Set VM node affinity by backplane IP, lan IP, and peer ID
  scale_computing.hypercore.vm_node_affinity:
    vm_name: demo-vm
    strict_affinity: true
    preferred_node:
      backplane_ip: "10.0.0.1"
      lan_ip: "10.0.0.1"
      peer_id: 1
    backup_node:
      backplane_ip: "10.0.0.2"
      lan_ip: "10.0.0.2"
      peer_id: 2

- name: Set strict affinity to false and delete the nodes
  scale_computing.hypercore.vm_node_affinity:
    vm_name: demo-vm
    strict_affinity: false
    preferred_node:
      node_uuid: ""
    backup_node:
      node_uuid: ""
"""

RETURN = r"""
msg:
  description:
    - Info about node affinity update status.
  returned: always
  type: str
  sample:
    msg: "Node affinity successfully updated."
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.node import Node
from ..module_utils.utils import get_query
from ..module_utils.task_tag import TaskTag


def get_node_uuid(module, node, rest_client):
    if module.params[node] and any(
        value == "" for value in module.params[node].values()
    ):  # delete node
        node_uuid = ""
        return node_uuid
    if module.params[node] and any(
        value is not None for value in module.params[node].values()
    ):  # if node is provided and not "", and at least one of it's parameters isn't None
        # if all parameters are set to None, query will be set to {} thus returning existing node
        query = get_query(
            module.params[node],
            "node_uuid",  # uuid is checked if it really exists
            "backplane_ip",
            "lan_ip",
            "peer_id",
            ansible_hypercore_map=dict(
                node_uuid="uuid",
                backplane_ip="backplaneIP",
                lan_ip="lanIP",
                peer_id="peerID",
            ),
        )
        node = Node.get_node(query, rest_client, must_exist=True)
        node_uuid = node.node_uuid
        return node_uuid


def set_parameters_for_payload(module, vm, rest_client):
    strict_affinity = module.params["strict_affinity"]
    preferred_node_uuid = get_node_uuid(module, "preferred_node", rest_client)
    backup_node_uuid = get_node_uuid(module, "backup_node", rest_client)
    if preferred_node_uuid is None:  # node is not provided
        preferred_node_uuid = vm.node_affinity["preferred_node"]["node_uuid"]
        if vm.node_affinity["preferred_node"]["node_uuid"]:  # Check if exists
            Node.get_node(
                {"uuid": vm.node_affinity["preferred_node"]["node_uuid"]},
                rest_client,
                must_exist=True,
            )
    if backup_node_uuid is None:  # node is not provided
        backup_node_uuid = vm.node_affinity["backup_node"]["node_uuid"]
        if vm.node_affinity["backup_node"]["node_uuid"]:  # Check if exists
            Node.get_node(
                {"uuid": vm.node_affinity["backup_node"]["node_uuid"]},
                rest_client,
                must_exist=True,
            )
    return strict_affinity, preferred_node_uuid, backup_node_uuid


def run(module, rest_client):
    vm = VM.get_by_name(
        module.params, rest_client, must_exist=True
    )  # get vm from vm_name

    strict_affinity, preferred_node_uuid, backup_node_uuid = set_parameters_for_payload(
        module, vm, rest_client
    )

    if strict_affinity is True and preferred_node_uuid == "" and backup_node_uuid == "":
        raise errors.VMInvalidParams

    if (
        vm.node_affinity["strict_affinity"] == strict_affinity
        and vm.node_affinity["preferred_node"]["node_uuid"] == preferred_node_uuid
        and vm.node_affinity["backup_node"]["node_uuid"] == backup_node_uuid
    ):
        msg = "Node affinity already set to desired values."
        return (
            False,
            msg,
            dict(before=None, after=None),
        )

    payload = {
        "affinityStrategy": {
            "strictAffinity": strict_affinity,
            "preferredNodeUUID": preferred_node_uuid,
            "backupNodeUUID": backup_node_uuid,
        }
    }
    endpoint = "{0}/{1}".format("/rest/v1/VirDomain", vm.uuid)
    task_tag = rest_client.update_record(endpoint, payload, module.check_mode)
    TaskTag.wait_task(rest_client, task_tag)
    vm_after = VM.get_by_name(module.params, rest_client, must_exist=True)
    if module.check_mode:
        vm_after.node_affinity = dict(
            strict_affinity=strict_affinity,
            preferred_node=Node.get_node(
                {"uuid": preferred_node_uuid}, rest_client
            ).to_ansible()
            if preferred_node_uuid != ""
            else None,
            backup_node=Node.get_node(
                {"uuid": backup_node_uuid}, rest_client
            ).to_ansible()
            if backup_node_uuid != ""
            else None,
        )
    msg = "Node affinity successfully updated."
    return (
        True,
        msg,
        dict(before=vm.node_affinity, after=vm_after.node_affinity),
    )


def main():
    module = AnsibleModule(
        supports_check_mode=False,
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
                options=dict(
                    node_uuid=dict(type="str"),
                    backplane_ip=dict(type="str"),
                    lan_ip=dict(type="str"),
                    # option types need to be provided so that in case of "peer_id: "{{ nodes.records[0].peer_id }}"" peer_id is int and not str
                    peer_id=dict(type="int"),
                ),
            ),
            backup_node=dict(
                type="dict",
                options=dict(
                    node_uuid=dict(type="str"),
                    backplane_ip=dict(type="str"),
                    lan_ip=dict(type="str"),
                    peer_id=dict(type="int"),
                ),
            ),
        ),
    )

    try:
        client = Client(
            host=module.params["cluster_instance"]["host"],
            username=module.params["cluster_instance"]["username"],
            password=module.params["cluster_instance"]["password"],
        )
        rest_client = RestClient(client)
        changed, msg, diff = run(module, rest_client)
        module.exit_json(changed=changed, msg=msg, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
