#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_params

author:
  - Polona Mihalič (@PolonaM)
short_description: Manage VM's parameters
description:
  - Update VM's name, description, tags, memory, number of CPUs.
  - Change VM's power state.
  - Assign snapshot schedule to the VM.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  vm_name:
    description:
      - VM's name.
      - Serves as unique identifier.
    type: str
    required: true
  vm_name_new:
    description:
      - VM's new name.
    type: str
  description:
    description:
      - VM's description.
    type: str
  tags:
    description:
      - User-modifiable words for organizing a group of VMs. Multiple tags should be provided as list.
      - All existing tags will be overwritten, so group tag should always be included.
    type: list
    elements: str
  memory:
    description:
      - Amount of memory reserved, in bytes.
      - May only be modified if VM is in C(SHUTOFF) or C(CRASHED) state.
    type: int
  vcpu:
    description:
      - Number of allotted virtual CPUs.
      - May only be modified if VM is in C(SHUTOFF) or C(CRASHED) state.
    type: int
  power_state:
    description:
      - Desired VM state.
      - States C(PAUSE) and C(LIVEMIGRATE) are not exposed in this module (this can be done with raw api module).
    choices: [ start, shutdown, stop, reboot, reset ]
    type: str
  snapshot_schedule:
    description:
      - The name of an existing snapshot_schedule to assign to VM.
      - VM can have 0 or 1 snapshot schedules assigned.
    type: str
"""


EXAMPLES = r"""
- name: Set VM simple params
  scale_computing.hypercore.vm_params:
    vm_name: demo-vm
    vm_name_new: renamed-vm
    description: test vm params
    tags:
      - Group-name
      - tag1
      - tag2
    memory: "{{ '512 MB' | human_to_bytes }}"
    vcpu: 2
    power_state: shutdown
    snapshot_schedule: demo-snap-schedule

- name: Delete description, tags and snapshot_schedule
  scale_computing.hypercore.vm_params:
    vm_name: demo-vm
    description: ""
    tags: [""]
    snapshot_schedule: ""
"""


RETURN = r"""
reboot_needed:
  description:
      - Info if reboot is needed after VM parameters update.
  returned: success
  type: bool
  sample:
      reboot_needed: true
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments
from ..module_utils.errors import ScaleComputingError
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM, ManageVMParams


def run(module, rest_client):
    vm = VM.get_by_name(module.params, rest_client, must_exist=True)
    changed, reboot_needed, diff = ManageVMParams.set_vm_params(module, rest_client, vm)
    return changed, reboot_needed, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            vm_name_new=dict(
                type="str",
            ),
            description=dict(
                type="str",
            ),
            tags=dict(type="list", elements="str"),
            memory=dict(
                type="int",
            ),
            vcpu=dict(
                type="int",
            ),
            power_state=dict(
                type="str",
                choices=["start", "shutdown", "stop", "reboot", "reset"],
            ),
            snapshot_schedule=dict(
                type="str",
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]
        client = Client(host, username, password)
        rest_client = RestClient(client)
        changed, reboot_needed, diff = run(module, rest_client)
        module.exit_json(changed=changed, reboot_needed=reboot_needed, diff=diff)
    except ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
