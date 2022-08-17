#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_replication

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Plugin handles actions over network interfaces
description:
  - Plugin enables actions over network interfaces on a specified virtual machine
  - Can create, update, delete specified network interfaces
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  state:
    description:
      - State defines which operation should plugin do over selected network interfaces
      - present, absent, set
    choices: [ present, absent, set ]
    type: str
    required: True
  vm_name:
    description:
      - Virtual machine name
      - Used to identify selected virtual machine by name
    type: str
  vm_uuid:
    description:
      - Virtual machine uniquie identifier
      - Used to identify selected virtual machine by uuid
    type: str
  items:
    description:
      - List of network interfaces
    type: list
    elements: dict
"""

EXAMPLES = r"""
- name: Retrieve all VMs
  scale_computing.hypercore.sample_vm_info:
  register: result

- name: Retrieve all VMs with specific name
  scale_computing.hypercore.sample_vm_info:
    name: vm-a
  register: result
"""

RETURN = r"""
vms:
  description:
    - A list of VMs records.
  returned: success
  type: list
  sample:
    - name: "vm-name"
      uuid: "1234-0001"
      state: "running"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.replication import Replication
from ..module_utils.state import ReplicationState
from ..module_utils.vm import VM


def ensure_enabled_or_reenabled(module, rest_client):
    changed = False
    response = {}
    virtual_machine_obj_list = VM.get(query={"name": module.params["vm_name"]}, rest_client=rest_client)
    if not virtual_machine_obj_list:
      errors.VMNotFound(module.params["vm_name"])
    existing_replication_obj_list = Replication.get(rest_client=rest_client, query={"sourceDomainUUID": virtual_machine_obj_list[0].uuid})
    if existing_replication_obj_list: # Update existing
        #TODO: remote_cluster_connection_uuid rename after cluster_info is implemented
        if (module.params["remote_cluster"] is None or existing_replication_obj_list[0].remote_cluster_connection_uuid == module.params["remote_cluster"]) and existing_replication_obj_list[0].state != ReplicationState.enabled:
            existing_replication_obj_list[0].state = ReplicationState.enabled
            data = existing_replication_obj_list[0].to_hypercore()
            response = rest_client.update_record(endpoint="/rest/v1/VirDomainReplication/"+existing_replication_obj_list[0].replication_uuid, payload=data, check_mode=False)
            changed = True
        elif module.params["remote_cluster"] is not None and existing_replication_obj_list[0].remote_cluster_connection_uuid != module.params["remote_cluster"]:
            raise errors.ReplicationNotUnique(virtual_machine_obj_list[0].name)
    else: # Create replication
        new_replication_obj = Replication.from_ansible(ansible_data=module.params, virtual_machine_obj=virtual_machine_obj_list[0])
        data = new_replication_obj.to_hypercore()
        response = rest_client.create_record(endpoint="/rest/v1/VirDomainReplication", payload=data, check_mode=False)
        changed = True
    return changed, {"taskTag": response["taskTag"]} if "taskTag" in response.keys() else {}


def ensure_disabled(module, rest_client):
    changed = False
    response = {}
    virtual_machine_obj_list = VM.get(query={"name": module.params["vm_name"]}, rest_client=rest_client)
    if not virtual_machine_obj_list:
      raise errors.VMNotFound(module.params["vm_name"])
    existing_replication_obj_list = Replication.get(rest_client=rest_client, query={"sourceDomainUUID": virtual_machine_obj_list[0].uuid})
    if existing_replication_obj_list and existing_replication_obj_list[0].state != ReplicationState.disabled:
      existing_replication_obj_list[0].state = ReplicationState.disabled
      data = existing_replication_obj_list[0].to_hypercore()
      response = rest_client.update_record(endpoint="/rest/v1/VirDomainReplication/"+existing_replication_obj_list[0].replication_uuid, payload=data, check_mode=False)
      changed = True
    return changed, {"taskTag": response["taskTag"]} if "taskTag" in response.keys() else {}


def run(module, client, rest_client):
    if module.params["state"] in [ReplicationState.enabled, ReplicationState.reenabled]:
        return ensure_enabled_or_reenabled(module, rest_client)
    else:
        return ensure_disabled(module, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                required=True,
                choices=["enabled", "disabled", "reenabled"],
            ),
            vm_name=dict(
                type="str",
                required=True,
            ),
            remote_cluster=dict(
                type="str",
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        rest_client = RestClient(client=client)
        changed, debug_task_tag = run(module, client, rest_client)
        module.exit_json(changed=changed, debug_task_tag=debug_task_tag)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
