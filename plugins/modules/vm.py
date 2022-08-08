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
  - scale_computing.hc3.cluster_instance
seealso: []
options:
  name:
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
  attachGuestToolsISO:
    description:
      - If supported by operating system, create an extra device to attach the Scale Guest OS tools ISO
    type: bool
"""

EXAMPLES = r"""
- name: Create a VM
  scale_computing.hc3.vm:
    name: demo-vm
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
    name: "vm-name"
    uuid: "1234-0001"
    state: "running"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.vm import VM


# @Jure / @Justin define how we want to handle boot_device at VM creation
def parse_boot_device_list_to_str(boot_device_list):
    return []


def create_vm_body(virtual_machine):
    vm_body = {}
    optional = {}
    temp_dict = virtual_machine.serialize()
    optional["attachGuestToolsISO"] = temp_dict["attachGuestToolsISO"]
    temp_dict.pop("attachGuestToolsISO")
    vm_body["dom"] = temp_dict
    vm_body["options"] = optional
    return vm_body


def create_vm_update_body(virtual_machine):
    update_body = virtual_machine.serialize()
    update_body.pop("attachGuestToolsISO")
    return update_body


def run(module, client):
    end_point = "/rest/v1/VirDomain"

    new_virtual_machine = VM(client=client, vm_dict=module.params)
    existing_virtual_machines = VM.get(client=client, name=new_virtual_machine.name)
    if not existing_virtual_machines:
        data = create_vm_body(new_virtual_machine)
        json_response = client.request("POST", end_point, data=data).json
    else:  # TODO check if VM needs to be updated ()
        end_point += "/" + existing_virtual_machines[0]["uuid"]
        data = create_vm_update_body(new_virtual_machine)
        json_response = client.request("PATCH", end_point, data=data).json

    return json_response


def main():
    module = AnsibleModule(
        supports_check_mode=True,  # False ATM
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(
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
                    # TODO check those options
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
            tags=dict(
                type="list",
                elements="str"
            ),
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
            # TODO we want attachGuestToolsISO or attach_guest_tools_iso ? Consistency - attach_guest_tools_iso.
            attachGuestToolsISO=dict(
                type="bool",
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        vms = run(module, client)
        module.exit_json(changed=False, vms=vms)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
