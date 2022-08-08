#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_nic_info

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Returns info about nic.
description:
  - Returns info about all or specific nic on a selected virtual device.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hc3.cluster_instance
seealso: []
options:
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
  vlan:
    description:
      - Vlan on which network interface is operating on
      - Used to identify specific network interface
      - If included only network interface with the specified vlan will be returned
    type: int
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
from ..module_utils.vm import VM
from ..module_utils.utils import validate_uuid


def check_parameters(module):
    if module.params["vm_uuid"]:
        validate_uuid(module.params["vm_uuid"])


def create_vm_object(
    module, client
):  # if we decide to use vm_name and vm_uuid across all playbooks we can add this to .get method in VM class
    if module.params["vm_uuid"]:
        virtual_machine_dict = VM.get(client, uuid=module.params["vm_uuid"])[0]
    else:
        virtual_machine_dict = VM.get(client, name=module.params["vm_name"])[0]
    virtual_machine = VM(client=client, vm_dict=virtual_machine_dict)
    return virtual_machine


def run(module, client):
    check_parameters(module)
    if module.params["vlan"]:
        virtual_machine = create_vm_object(module, client)
        json_response = virtual_machine.find_net_dev(module.params["vlan"]).serialize()
    else:
        response_net_dev_list = []
        virtual_machine = create_vm_object(module, client)
        for net_dev in virtual_machine.net_devs_list:
            response_net_dev_list.append(net_dev.serialize())
        json_response = response_net_dev_list
    return json_response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
            ),
            vm_uuid=dict(
                type="str",
            ),
            vlan=dict(
                type="int",
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
        # We do not want to just show complete API response to end user.
        # Because API response content changes with HC3 version.
        module.exit_json(changed=False, vms=vms)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
