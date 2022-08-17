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
  - Domen Dobnikar (@domen_dobnikar)
short_description: Create or update virtual machine
description:
  - Module creates a new virtual machine or updates existing virtual machine.
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
  description:
    description:
      - Virtual machine description
    type: str
  memory:
    description:
      - Virtual machine physical memory in bytes
    type: int
    required: True
  vcpu:
    description:
      - Number of Central processing units on a virtual machine
    type: int
    required: True
  power_state:
    description:
      - Virtual machine power state
    choices: [ running, blocked, paused, shutdown, shutoff, crashed ]
    type: str
  state:
    description:
      - State defines which operation should plugin do over selected virtual machine
    choices: [ present, absent ]
    type: str
    required: True
  tags:
    description:
      - Tags define in which groups does a virtual machine belong to
    type: list
    elements: str
  disks:
    description:
      - Defines information about disks
    type: list
    elements: dict
  nics:
    description:
      - Defines information about network interfaces
    type: list
    elements: dict
  boot_devices:
    description:
      - Defines which devices should be selected as boot devices and in which order
    type: list
    elements: dict
  cloud_init:
    description:
      - Configuration data to be used by cloud-init (Linux) or cloudbase-init (Windows)
    type: dict
  attach_guest_tools_iso:
    description:
      - If supported by operating system, create an extra device to attach the Scale Guest OS tools ISO
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Create a VM
  scale_computing.hypercore.vm:
    vm_name: demo-vm
    # TODO
  register: result
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
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.state import VMState
from ..module_utils.utils import filter_dict, transform_ansible_to_hypercore_query
from ..module_utils.task_tag import TaskTag


def ensure_absent(module, client, rest_client):
    ansible_query = filter_dict(module.params, "vm_name")
    hypercore_query = transform_ansible_to_hypercore_query(
        ansible_query, dict(vm_name="name")
    )
    vm = rest_client.get_record("/rest/v1/VirDomain", hypercore_query, must_exist=False)
    if vm:
        task_tag = rest_client.delete_record(
            "{0}/{1}".format("/rest/v1/VirDomain", vm["uuid"]), module.check_mode
        )
        TaskTag.wait_task(RestClient(client), task_tag)
        return True, task_tag
    return False, dict(TaskTag="No Tag")


def ensure_present(module, client, rest_client):
    new_virtual_machine = VM.from_ansible(vm_dict=module.params)
    ansible_query = filter_dict(module.params, "vm_name")
    hypercore_query = transform_ansible_to_hypercore_query(
        ansible_query, dict(vm_name="name")
    )
    before = rest_client.get_record("/rest/v1/VirDomain", hypercore_query)
    if before:  # If the record already exists, update it using PATCH method
        task_tag = rest_client.update_record(
            "{0}/{1}".format("/rest/v1/VirDomain", before["uuid"]),
            new_virtual_machine.update_payload_to_hc3(),
            module.check_mode,
        )
    else:  # The record doesn't exist; Create it using POST with specified data
        task_tag = rest_client.create_record(
            "/rest/v1/VirDomain",
            new_virtual_machine.create_payload_to_hc3(),
            module.check_mode,
        )
    TaskTag.wait_task(RestClient(client), task_tag)
    return True, task_tag


def run(module, client, rest_client):
    if module.params["state"] == VMState.absent:
        return ensure_absent(module, client, rest_client)
    return ensure_present(module, client, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,  # False ATM
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            description=dict(
                type="str",
            ),
            memory=dict(
                type="int",
                required=True,
            ),
            vcpu=dict(
                type="int",
                required=True,
            ),
            power_state=dict(
                type="str",
                choices=[
                    # TODO (domen): check those options
                    "running",
                    "blocked",
                    "paused",
                    "shutdown",
                    "shutoff",
                    "crashed",
                ],
            ),
            state=dict(
                type="str",
                choices=[
                    "present",
                    "absent",
                ],
                required=True,
            ),
            tags=dict(type="list", elements="str"),
            disks=dict(
                type="list",
                elements="dict",
            ),
            nics=dict(
                type="list",
                elements="dict",
            ),
            boot_devices=dict(
                type="list",
                elements="dict",
            ),
            cloud_init=dict(
                type="dict",
            ),
            attach_guest_tools_iso=dict(
                type="bool",
                default=False,
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        rest_client = RestClient(client)
        changed, debug_task_tag = run(module, client, rest_client)
        module.exit_json(changed=changed, debug_task_tag=debug_task_tag)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
