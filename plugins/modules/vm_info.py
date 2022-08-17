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
  - Tjaž Eržen (@tjazsch)
short_description: Return info about virtual machines
description:
  - Plugin return information about all or specific virtual machines in a cluster.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  uuid:
    description:
      - Virtual machine unique identifier.
    type: str
  vm_name:
    description:
      - Virtual machine name
      - Used to identify selected virtual machine by name.
    type: str
"""

# TODO (domen): Update EXAMPLES
EXAMPLES = r"""
- name: Retrieve all VMs
  scale_computing.hypercore.sample_vm_info:
    host: 'Host IP address'
    username: 'Your scale cluster username'
    password: 'Your scale cluster password'
  register: result

- name: Retrieve all VMs with specific UUID
  scale_computing.hypercore.sample_vm_info:
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
      "vm_name": "XLAB-CentOS-7-x86_64-GenericCloud-2111"
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
from ..module_utils.utils import filter_dict
from ..module_utils.rest_client import RestClient


def run(module, rest_client):
    query = filter_dict(module.params, "uuid", "vm_name")
    return [
        VM.from_hypercore(vm_dict=vm_dict).to_ansible()
        for vm_dict in rest_client.list_records("/rest/v1/VirDomain", query)
    ]


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            uuid=dict(type="str"),
            vm_name=dict(type="str"),
        ),
        mutually_exclusive=[
            ("uuid", "vm_name"),
        ],
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]
        client = Client(host, username, password)
        rest_client = RestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
