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
  - scale_computing.hc3.cluster_instance
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
  scale_computing.hc3.sample_vm_info:
  register: result

- name: Retrieve all VMs with specific name
  scale_computing.hc3.sample_vm_info:
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
from ..module_utils.net_dev import NetDev
from ..module_utils.state import State
from ..module_utils.utils import validate_uuid


def check_parameters(module):
    if module.params["vm_uuid"]:
        validate_uuid(module.params["vm_uuid"])


def create_nic(client, end_point, net_dev):
    request_body = net_dev.serialize()
    json_response = client.request("POST", end_point, data=request_body).json
    return json_response


def update_nic(client, end_point, new_net_dev):
    request_body = new_net_dev.serialize()
    json_response = client.request("PATCH", end_point, data=request_body).json
    return json_response


def delete_nic(client, end_point):
    json_response = client.request("DELETE", end_point).json
    return json_response


def create_nic_uuid_list(module):
    net_dev_uuid_list = []
    if module.params["items"]:
        for net_dev in module.params["items"]:
            if "vlan_new" in net_dev.keys():
                net_dev_uuid_list.append(net_dev["vlan_new"])
            else:
                net_dev_uuid_list.append(net_dev["vlan"])
    return net_dev_uuid_list


def delete_not_used_nics(module, client, end_point, virtual_machine):
    nic_uuid_list = create_nic_uuid_list(module)
    for net_dev in virtual_machine.net_devs_list:
        if net_dev.vlan not in nic_uuid_list:
            json_response = delete_nic(client, end_point + "/" + net_dev.uuid)
            TaskTag.wait_task(client, json_response)


def create_vm(
    module, client
):  # if we decide to use vm_name and vm_uuid across all playbooks we can add this to .get method in VM class
    if module.params["vm_uuid"]:
        virtual_machine = VM(
            client=client, vm_dict=VM.get(client, uuid=module.params["vm_uuid"])[0]
        )
    else:
        virtual_machine = VM(
            client=client, vm_dict=VM.get(client, name=module.params["vm_name"])[0]
        )
    return virtual_machine


def do_present_or_set(client, end_point, existing_net_dev, new_net_dev):
    if existing_net_dev and not NetDev.compare(existing_net_dev, new_net_dev):
        json_response = update_nic(
            client, end_point + "/" + existing_net_dev.uuid, new_net_dev
        )
    else:
        json_response = create_nic(client, end_point, new_net_dev)
    return json_response


def do_absent(client, end_point, existing_net_dev):
    json_response = delete_nic(client, end_point + "/" + existing_net_dev.uuid)
    return json_response


def check_state_decide_action(module, client, state):
    end_point = "/rest/v1/VirDomainNetDevice"
    json_response = "No changes"
    virtual_machine = create_vm(module, client)

    if module.params["items"]:
        for net_dev in module.params["items"]:
            net_dev["vm_uuid"] = virtual_machine.uuid
            net_dev = NetDev(client=client, net_dev_dict=net_dev)
            if net_dev.vlan:
                existing_net_dev = virtual_machine.find_net_dev(vlan=net_dev.vlan)
            elif net_dev.mac:
                existing_net_dev = virtual_machine.find_net_dev(vlan=net_dev.mac)
            else:
                raise errors.MissingValue("VLAN and MAC in vm_nic.py ")
            if state in [State.present, State.set]:
                json_response = do_present_or_set(
                    client, end_point, existing_net_dev, net_dev
                )
            else:
                json_response = do_absent(client, end_point, existing_net_dev)
            TaskTag.wait_task(client, json_response)
    if state == State.set:
        updated_virtual_machine = create_vm(
            module, client
        )  # VM was updated, so we need to get the updated data from server
        delete_not_used_nics(module, client, end_point, updated_virtual_machine)
    return json_response


def run(module, client):
    check_parameters(module)

    json_response = check_state_decide_action(module, client, module.params["state"])

    return json_response


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
        vms = run(module, client)
        module.exit_json(changed=True, vms=vms)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
