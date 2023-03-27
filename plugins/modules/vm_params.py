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
  - Use vm_params to update VM's name, description, tags, memory, number of CPUs or change VM's power state.
  - Can also be used to assign a snapshot schedule to the VM.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
  - scale_computing.hypercore.force_reboot
seealso: []
options:
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
      - States C(PAUSE) and C(LIVEMIGRATE) are not exposed in this module
        (this can be done with raw api module).
      - Note that
        - I(shutdown) will trigger a graceful ACPI shutdown.
        - I(reboot) will trigger a graceful ACPI reboot.
        - I(stop) will trigger an abrupt shutdown (force power off).
          VM might loose data, and filesystem might be corrupted afterwards.
        - I(reset) will trigger an abrupt reset (force power reset).
          VM might loose data, and filesystem might be corrupted afterwards.
    choices: [ start, shutdown, stop, reboot, reset ]
    type: str
  operating_system:
    description:
      - Operating system name.
      - Used to select drivers package
    type: str
    choices: [ os_windows_server_2012, os_other ]
  snapshot_schedule:
    description:
      - The name of an existing snapshot_schedule to assign to VM.
      - VM can have 0 or 1 snapshot schedules assigned.
    type: str
notes:
  - C(check_mode) is not supported.
"""


EXAMPLES = r"""
- name: Set VM simple params
  scale_computing.hypercore.vm_params:
    vm_name: demo-vm
    vm_name_new: renamed-vm
    description: test vm params
    force_reboot: true
    shutdown_timeout: "{{ '5minutes' | community.general.to_time_unit('seconds') }}"
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
vm_rebooted:
  description:
      - Info if reboot of the VM was performed.
  returned: success
  type: bool
  sample: true
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments
from ..module_utils.errors import ScaleComputingError
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM, ManageVMParams


def run(module, rest_client):
    vm = VM.get_by_old_or_new_name(module.params, rest_client, must_exist=True)
    # Update VM's name, description, tags, memory, number of CPUs, power_state and/or assign snapshot schedule.
    # In case if reboot is needed, set_vm_params will shutdown the vm
    # In case if reboot is not needed, set_vm_params will set power_state as specified in the module.params["power_state"]
    changed, reboot, diff = ManageVMParams.set_vm_params(module, rest_client, vm)
    if module.params["power_state"] not in ["shutdown", "stop"]:
        # VM will be powered on in case if reboot is needed and module.params["power_state"] in ["start", "reboot", "reset"]
        # if reboot is not needed, vm_power_up doesn't do anything
        vm.vm_power_up(module, rest_client)
    else:
        reboot = False
    return changed, reboot, diff


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
            force_reboot=dict(
                type="bool",
                default=False,
            ),
            shutdown_timeout=dict(
                type="float",
                default=300,
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
            operating_system=dict(
                type="str",
                choices=["os_windows_server_2012", "os_other"],
            ),
            snapshot_schedule=dict(
                type="str",
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, reboot, diff = run(module, rest_client)
        module.exit_json(changed=changed, vm_rebooted=reboot, diff=diff)
    except ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
