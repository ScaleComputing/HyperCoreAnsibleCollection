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
short_description: Returns info about replication of a specific VM
description:
  - Returns information about replication of a specific virtual machine, if replication is configured.
version_added: 1.0.0
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
  returned: success
  type: list
  elements: dict
  contains:
    vm_name:
      description: Virtual machine name identifier
      type: str
      sample: demo-vm
    remote_cluster:
      description: Remote cluster name
      type: str
      sample: PUB4
    state:
      description: The desired state of the VM replication
      type: str
      sample: enabled
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.replication import Replication


def run(module, rest_client):
    if not module.params["vm_name"]:
        records = [
            replication_obj.to_ansible()
            for replication_obj in Replication.get(rest_client=rest_client, query=None)
        ]
    else:
        virtual_machine_obj_list = VM.get_or_fail(
            query={"name": module.params["vm_name"]}, rest_client=rest_client
        )
        replication_list = Replication.get(
            query={"sourceDomainUUID": virtual_machine_obj_list[0].uuid},
            rest_client=rest_client,
        )
        if not replication_list:
            # No replication found for specified VM
            return False, []
        records = [replication_list[0].to_ansible()]
    return False, records


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
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, records = run(module, rest_client)
        module.exit_json(changed=changed, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
