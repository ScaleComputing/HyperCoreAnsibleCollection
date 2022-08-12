#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_nic

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
from ..module_utils.task_tag import TaskTag
from ..module_utils.vm import VM
from ..module_utils.nic import Nic
from ..module_utils.state import State
from ..module_utils.utils import validate_uuid


def check_parameters(module):
    if module.params["vm_uuid"]:
        validate_uuid(module.params["vm_uuid"])


def create_nic(client, end_point, nic):
    request_body = nic.data_to_hc3()
    json_response = client.request("POST", end_point, data=request_body).json
    return json_response


def update_nic(client, end_point, new_nic):
    request_body = new_nic.data_to_hc3()
    json_response = client.request("PATCH", end_point, data=request_body).json
    return json_response


def delete_nic(client, end_point):
    json_response = client.request("DELETE", end_point).json
    return json_response


def create_nic_uuid_list(module):
    new_nic_uuid_list = []
    if module.params["items"]:
        for nic in module.params["items"]:
            if "vlan_new" in nic.keys():
                new_nic_uuid_list.append(nic["vlan_new"])
            else:
                new_nic_uuid_list.append(nic["vlan"])
    return new_nic_uuid_list


def delete_not_used_nics(module, client, end_point, virtual_machine):
    nic_uuid_list = create_nic_uuid_list(module)
    for nic in virtual_machine.nic_list:
        if nic.vlan not in nic_uuid_list:
            json_response = delete_nic(client, end_point + "/" + nic.uuid)
            TaskTag.wait_task(client, json_response)


def find_vm(
    module, client
):  # if we decide to use vm_name and vm_uuid across all playbooks we can add this to .get method in VM class
    if "vm_uuid" in module.params.keys() and module.params["vm_uuid"]:
        virtual_machine = VM(
            from_hc3=True,
            vm_dict=VM.get(client, uuid=module.params["vm_uuid"])[0],
            client=client,
        )
    else:
        virtual_machine = VM(
            from_hc3=True,
            vm_dict=VM.get(client, name=module.params["vm_name"])[0],
            client=client,
        )
    return virtual_machine


def ensure_present_or_set(client, end_point, existing_hc3_nic, new_nic):
    if existing_hc3_nic and not existing_hc3_nic.is_update_needed(new_nic):
        json_response = update_nic(
            client, end_point + "/" + existing_hc3_nic.uuid, new_nic
        )
    elif not existing_hc3_nic:
        json_response = create_nic(client, end_point, new_nic)
    else:
        return {}
    return json_response


def ensure_absent(client, end_point, existing_hc3_nic):
    # TODO check if nic exists other return changed=False and No task tag
    # TODO add integration test for this specific bug
    if existing_hc3_nic:
        json_response = delete_nic(client, end_point + "/" + existing_hc3_nic.uuid)
        return json_response
    return {}


def check_state_decide_action(module, client, state):
    end_point = "/rest/v1/VirDomainNetDevice"
    json_response = {}
    virtual_machine = find_vm(module, client)

    if module.params["items"]:
        for nic in module.params["items"]:
            nic["vm_uuid"] = virtual_machine.uuid
            nic = Nic.create_from_ansible(nic_dict=nic)
            if nic.vlan is not None:
                # TODO we have vlan_new and mac_new - corner case
                # TODO integration test to check this corner cases
                existing_hc3_nic = virtual_machine.find_nic(vlan=nic.vlan)
            elif nic.mac:
                existing_hc3_nic = virtual_machine.find_nic(vlan=nic.mac)
            else:
                raise errors.MissingValueAnsible(
                    "VLAN and MAC - vm_nic.py - check_state_decide_action()"
                )
            if state in [State.present, State.set]:
                json_response = ensure_present_or_set(
                    client, end_point, existing_hc3_nic, nic
                )
            else:
                json_response = ensure_absent(client, end_point, existing_hc3_nic)
            if "taskTag" in json_response.keys():
                TaskTag.wait_task(client, json_response)
    if state == State.set:
        updated_virtual_machine = find_vm(
            module, client
        )  # VM was updated, so we need to get the updated data from server
        delete_not_used_nics(module, client, end_point, updated_virtual_machine)
    return json_response


def create_output(json_response):
    if "taskTag" in json_response.keys():
        return True, {"taskTag": json_response["taskTag"]}
    return True, {}


def run(module, client):
    check_parameters(module)

    json_response = check_state_decide_action(module, client, module.params["state"])

    return create_output(json_response)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                required=True,
                choices=["present", "absent", "set"],
            ),
            vm_uuid=dict(
                type="str",
            ),
            vm_name=dict(
                type="str",
            ),
            items=dict(
                type="list",
                elements="dict",
            ),
        ),
        mutually_exclusive=[
            ("vm_name", "vm_uuid"),
        ],
        required_one_of=[("vm_name", "vm_uuid")],
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        changed, debug_task_tag = run(module, client)
        module.exit_json(changed=changed, debug_task_tag=debug_task_tag)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
