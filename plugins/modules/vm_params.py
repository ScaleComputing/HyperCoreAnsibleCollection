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
  - Update VM's name, description, tags, memory, number of CPU.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  vm_name:
    description:
      - Virtual machine's name.
      - Serves as unique identifier.
    type: str
    required: true
  vm_name_new:
    description:
      - Virtual machine's new name.
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
      - May only be modified if the domain is in the VirDomainState.SHUTOFF or VirDomainState.CRASHED states
    type: int
  vcpu:
    description:
      - Number of allotted virtual CPUs.
      - May only be modified if the domain is in the SHUTOFF or CRASHED states
    type: int
  power_state:
    description:
      - Desired VM state
      - PAUSE and LIVEMIGRATE are possible in REST API, but module will not expose them.
        PAUSE is marked as internal, LIVEMIGRATE requires to specify destination node. It can be done with raw api module).
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
from ..module_utils.vm import VM
from ..module_utils.snapshot_schedule import SnapshotSchedule


REBOOT_LOOKUP = {
    "vm_name": False,
    "description": False,
    "tags": False,
    "memory": True,
    "vcpu": True,
    "power_state": False,
    "snapshot_schedule": True,
}


def build_payload(module, rest_client):
    payload = {}

    if module.params["vm_name_new"]:
        payload["name"] = module.params["vm_name_new"]
    if module.params["description"] is not None:  # we want to be able to write ""
        payload["description"] = module.params["description"]
    if module.params["tags"] is not None:  # we want to be able to write ""
        payload["tags"] = ",".join(module.params["tags"])  # tags is a list of strings
    if module.params["memory"]:
        payload["mem"] = module.params["memory"]
    if module.params["vcpu"]:
        payload["numVCPU"] = module.params["vcpu"]
    if module.params["snapshot_schedule"] is not None:  # we want to be able to write ""
        if module.params["snapshot_schedule"] == "":
            payload["snapshotScheduleUUID"] = ""
        else:
            query = {"name": module.params["snapshot_schedule"]}
            snapshot_schedule = SnapshotSchedule.get_snapshot_schedule(
                query, rest_client, must_exist=True
            )
            payload["snapshotScheduleUUID"] = snapshot_schedule.uuid

    return payload


def to_be_changed(vm, module):
    changed_params = {}
    if module.params["vm_name_new"]:
        changed_params["vm_name"] = vm.name != module.params["vm_name_new"]
    if module.params["description"] is not None:  # we want to be able to write ""
        changed_params["description"] = vm.description != module.params["description"]
    if module.params["tags"] is not None:  # we want to be able to write ""
        changed_params["tags"] = vm.tags != module.params["tags"]
    if module.params["memory"]:
        changed_params["memory"] = vm.mem != module.params["memory"]
    if module.params["vcpu"]:
        changed_params["vcpu"] = vm.numVCPU != module.params["vcpu"]
    if module.params["power_state"]:
        changed_params["power_state"] = (
            module.params["power_state"] not in vm.power_state
        )  # state in playbook is different than read from HC3 (start/started)
    if module.params["snapshot_schedule"] is not None:  # we want to be able to write ""
        if module.params["snapshot_schedule"] == "":
            changed_params["snapshot_schedule"] = vm.snapshot_schedule != ""
        else:
            changed_params["snapshot_schedule"] = (
                vm.snapshot_schedule != module.params["snapshot_schedule"]
            )

    return any(changed_params.values()), changed_params


def needs_reboot(module, changed):
    for param in module.params:
        if (
            module.params[param] is not None and param in REBOOT_LOOKUP
        ):  # skip not provided parameters and cluster_instance
            if REBOOT_LOOKUP[param] and changed[param]:
                return True
    return False


def build_after_diff(module, rest_client):
    after = {}
    if module.check_mode:
        if module.params["vm_name_new"]:
            after["vm_name"] = module.params["vm_name_new"]
        else:
            after["vm_name"] = module.params["vm_name"]
        if module.params["description"] is not None:
            after["description"] = module.params["description"]
        if module.params["tags"] is not None:
            after["tags"] = module.params["tags"]
        if module.params["memory"]:
            after["memory"] = module.params["memory"]
        if module.params["vcpu"]:
            after["vcpu"] = module.params["vcpu"]
        if module.params["power_state"]:
            after["power_state"] = module.params["power_state"]
        if module.params["snapshot_schedule"] is not None:
            after["snapshot_schedule"] = module.params["snapshot_schedule"]
        return after
    query = {
        "name": module.params["vm_name_new"]
        if module.params["vm_name_new"]
        else module.params["vm_name"]
    }
    vm = VM.get_or_fail(query, rest_client)[0]
    after["vm_name"] = vm.name
    if module.params["description"] is not None:
        after["description"] = vm.description
    if module.params["tags"] is not None:
        after["tags"] = vm.tags
    if module.params["memory"]:
        after["memory"] = vm.mem
    if module.params["vcpu"]:
        after["vcpu"] = vm.numVCPU
    if module.params["power_state"]:
        after["power_state"] = vm.power_state
    if module.params["snapshot_schedule"] is not None:
        after["snapshot_schedule"] = vm.snapshot_schedule
    return after


def build_before_diff(vm, module):
    before = {"vm_name": vm.name}
    if module.params["description"] is not None:
        before["description"] = vm.description
    if module.params["tags"] is not None:
        before["tags"] = vm.tags
    if module.params["memory"]:
        before["memory"] = vm.mem
    if module.params["vcpu"]:
        before["vcpu"] = vm.numVCPU
    if module.params["power_state"]:
        before["power_state"] = vm.power_state
    if module.params["snapshot_schedule"] is not None:
        before["snapshot_schedule"] = vm.snapshot_schedule
    return before


def run(module, rest_client):
    vm = VM.get_by_name(module.params, rest_client, must_exist=True)
    changed, changed_parameters = to_be_changed(vm, module)
    if changed:
        payload = build_payload(module, rest_client)
        endpoint = "{0}/{1}".format("/rest/v1/VirDomain", vm.uuid)
        rest_client.update_record(endpoint, payload, module.check_mode)
        # power_state needs different endpoint
        # Wait_task in update_vm_power_state doesn't handle check_mode
        if module.params["power_state"] and not module.check_mode:
            vm.update_vm_power_state(module, rest_client, module.params["power_state"])
        reboot_needed = needs_reboot(module, changed_parameters)
        return (
            True,
            reboot_needed,
            dict(
                before=build_before_diff(vm, module),
                after=build_after_diff(module, rest_client),
            ),
        )
    else:
        reboot_needed = False
        return (
            False,
            reboot_needed,
            dict(before=None, after=None),
        )


def main():
    module = AnsibleModule(
        supports_check_mode=True,
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
