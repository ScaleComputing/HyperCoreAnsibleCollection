#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_info

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Sample plugin
description:
  - A sample plugin with boilerplate code.
version_added: 0.0.1
extends_documentation_fragment: []
seealso: []
options:
  host:
    description:
      - Host address.
    type: str
    required: true
  username:
    description:
      - Scale computing username
    type: str
    required: true
  password:
    description:
      - Scale computing password
    type: str
    required: true
  uuid:
    description:
      - VM UUID
      - If included only VMs with matching UUID will be returned.
    type: str
"""

EXAMPLES = r"""
- name: Retrieve all VMs
  scale_computing.hc3.sample_vm_info:
    host: 'Host IP address'
    username: 'Your scale cluster username'
    password: 'Your scale cluster password'
  register: result

- name: Retrieve all VMs with specific UUID
  scale_computing.hc3.sample_vm_info:
    host: 'Host IP address'
    username: 'Your scale cluster username'
    password: 'Your scale cluster password'
    uuid: 'valid virtual machine UUID'
  register: result
"""

RETURN = r"""
vms:
  description:
    - A list of VMs records.
  returned: success
  type: list
  sample:
    - "boot_devices":  # TODO check what we promised
            - "name": ""
              "disk_slot": 0
              "type": "virtio_disk"
              "uuid": "fec11a1d-e8e3-4a50-8b50-57dece3e8baf"
      "description": "XLAB-ac1-export-20220705T201528: "
      "disks":  # TODO check what we promised
            - "size": 8589934592
              "name": ""
              "disk_slot": 0
              "type": "virtio_disk"
              "uuid": "e8c8aa6b-1043-48a0-8407-2c432d705378"
              "memory": 536870912
      "name": "XLAB-CentOS-7-x86_64-GenericCloud-2111"
      "nics":
            - "type": "RTL8139"
              "uuid": "4c627449-99c6-475b-8e8e-9ae2587db5fc"
              "vlan": 0
      "vcpu": 2
      "power_state": "shutoff"
      "tags": "Xlab,ac1,us3"
      "uuid": "f0c91f97-cbfc-40f8-b918-ab77ae8ea7fb"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.vm import VM
from ..module_utils.utils import validate_uuid


def run(module, client): # if we decide to use vm_name and vm_uuid across all playbooks we can add most of this to .get method in VM class
    virtual_machine_info_list = []
    if module.params["uuid"]: # Search by uuid
      validate_uuid(module.params["uuid"])
      virtual_machine = VM(client=client, vm_dict=VM.get(client, uuid=module.params["uuid"])[0])
      virtual_machine_info_list = virtual_machine.create_vm_info_list()
    elif module.params["name"]: # Search by name
      virtual_machine = VM(client=client, vm_dict=VM.get(client, name=module.params["name"])[0])
      virtual_machine_info_list = virtual_machine.create_vm_info_list()
    else:                      # No name or uuid, we return all VMs
      #virtual_machine = VM(client=client)
      virtual_machines = VM.get(client) # List of all virtual machines in the cluster
      for virtual_machine in virtual_machines:
        virtual_machine = VM(client=client, vm_dict=virtual_machine)
        virtual_machine_info_list.append(virtual_machine.create_vm_info_list())

    return virtual_machine_info_list


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            uuid=dict(type="str"),
            name=dict(type="str"),
        ),
        mutually_exclusive=[
            ("uuid", "name"),
        ],
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
