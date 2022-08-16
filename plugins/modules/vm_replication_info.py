#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
module: vm_replication_info

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Returns info about replication on a specific virtual machine.
description:
  - Returns info about replication on a specific virtual machine, if replication is configured.
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
    required: False
"""

EXAMPLES = r"""
- name: Module vm_replication_info sample output
  scale_computing.hypercore.vm_replication_info:
    cluster_instance:
        host: 'host address'
        username: 'username'
        password: 'password'
    vm_name: XLAB-demo-vm-clone
  register: records
"""

RETURN = r"""
records:
  description:
    - The replication records.
  type: list
  returned: success
  sample:
    - vm_name: demo-vm
      remote_cluster: PUB4
      state: enabled
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.replication import Replication


def create_output(records):
    return False, records


def find_vm(client, vm_name):
    virtual_machine_list = VM.get(client=client, name=vm_name)
    if virtual_machine_list:
        virtual_machine = VM(from_hc3=True, vm_dict=virtual_machine_list[0])
        return virtual_machine
    raise errors.VMNotFound(vm_name)


def find_replication(rest_client, virtual_machine):
    if virtual_machine:
        replication = Replication.get(rest_client=rest_client, vm_uuid=virtual_machine.uuid)
        if replication:
            replication = Replication.create_from_hypercore(
                hypercore_data=replication[0], virtual_machine_obj=virtual_machine
            )
            return [replication.data_to_ansible()]
        return [{}]
    else:
        return Replication.get(rest_client=rest_client)


def run(module, client, rest_client):
    virtual_machine = None
    if module.params["vm_name"]:
        virtual_machine = find_vm(client, module.params["vm_name"])
    records = find_replication(rest_client, virtual_machine)
    return create_output(records)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=False,
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        rest_client = RestClient(client)
        changed, records = run(module, client, rest_client)
        module.exit_json(changed=changed, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
