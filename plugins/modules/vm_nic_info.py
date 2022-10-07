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
short_description: Returns info about NIC
description:
  - Returns the information about all or a specific NIC on a selected virtual machine.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
seealso: []
options:
  vlan:
    description:
      - VLAN on which network interface is operating on.
      - Used to identify specific network interface.
      - If included only network interface with the specified VLAN will be returned.
    type: int
"""

EXAMPLES = r"""
- name: Retrieve NIC info on VLAN 15
  scale_computing.hypercore.vm_nic_info:
    vm_name: 'XLAB-demo-vm'
    vlan: 15
  register: testout

- name: Retrieve NIC info on all vlans
  scale_computing.hypercore.vm_nic_info:
    vm_name: 'XLAB-demo-vm'
  register: testout
"""

RETURN = r"""
records:
  description:
    - A list of NICs records.
  returned: success
  type: list
  sample:
    - uuid: 07a2a68a-0afa-4718-9c6f-00a39d08b67e
      vlan: 15
      type: virtio
      mac: 12-34-56-78-AB
      connected: true
      ipv4_addresses: []
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.vm import VM
from ..module_utils.rest_client import RestClient


def run(module, rest_client):
    virtual_machine = VM.get_or_fail(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )[0]
    if not module.params["vlan"]:
        return False, [nic.to_ansible() for nic in virtual_machine.nic_list]
    return False, [virtual_machine.find_nic(module.params["vlan"])[0].to_ansible()]


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            vlan=dict(
                type="int",
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        rest_client = RestClient(client)
        changed, records = run(module, rest_client)
        module.exit_json(changed=changed, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
