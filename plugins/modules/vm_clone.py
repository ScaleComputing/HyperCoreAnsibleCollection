#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# language=yaml
DOCUMENTATION = r"""
module: vm_clone

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Handles cloning of the VM
description:
  - Use M(scale_computing.hypercore.vm_clone) to clone a specified virtual machine.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.cloud_init
seealso: []
options:
  vm_name:
    description:
      - Name of the VM clone.
      - Used to identify a clone of the virtual machine by name.
    type: str
    required: true
  source_vm_name:
    description:
      - Name of the source virtual machine, to be cloned.
      - Used to identify selected virtual machine by name.
    type: str
    required: true
  tags:
    description:
      - Virtual machine tags.
      - Used to group virtual machine.
    required: false
    type: list
    elements: str
  preserve_mac_address:
    description: Allows keeping same MAC addresses as in original VM.
    type: bool
    default: false
    version_added: 1.3.0
  source_snapshot_label:
    description: Allows cloning VM from a specific snapshot using snapshot label.
    type: str
    version_added: 1.3.0
  source_snapshot_uuid:
    description: Allows cloning VM from a specific snapshot using snapshot uuid.
    type: str
    version_added: 1.3.0
notes:
  - C(check_mode) is not supported.
"""

# language=yaml
EXAMPLES = r"""
- name: Clone VM
  scale_computing.hypercore.vm_clone:
    vm_name: demo-vm-clone
    source_vm_name: demo-vm
    cloud_init:
      user_data: "{{ lookup('file', 'cloud-init-user-data-example.yml') }}"
      meta_data: |
        # Content for cloud-init meta-data (or user-data) can be inline too.
    tags:
      - test
      - tag
  register: output
"""

# language=yaml
RETURN = r"""
msg:
  description:
    - Return message.
  returned: success
  type: str
  sample: Virtual machine - VM-TEST - cloning complete to - VM-TEST-clone
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.vm_snapshot import VMSnapshot as Snapshot
from ..module_utils.task_tag import TaskTag


# Check snapshot list, raise error if necessary.
def check_snapshot_list(module: AnsibleModule, snapshot_list: list) -> None:
    # No snapshot was found, raise error.
    if not snapshot_list or not snapshot_list[0].get("snapshot_uuid"):
        if module.params["source_snapshot_label"]:
            raise errors.ScaleComputingError(
                f"Snapshot with label - {module.params['source_snapshot_label']} - not found."
            )
        else:
            raise errors.ScaleComputingError(
                f"Snapshot with uuid - {module.params['source_snapshot_uuid']} - not found."
            )

    # More than one snapshot was found, raise error.
    if snapshot_list and len(snapshot_list) > 1:
        raise errors.ScaleComputingError(
            f"More than one snapshot exists with label - {module.params['source_snapshot_label']}, please use specify source_snapshot_uuid instead."
        )


def get_snapshot(
    module: AnsibleModule, rest_client: RestClient, virtual_machine_obj: VM
) -> AnsibleModule:
    snapshot_list = []
    # Get snapshot from uuid.
    if module.params["source_snapshot_uuid"]:
        snapshot_list = Snapshot.get_snapshots_by_query(
            dict(
                uuid=module.params["source_snapshot_uuid"],
                domainUUID=virtual_machine_obj.uuid,
            ),
            rest_client,
        )
    # Get snapshot from label.
    elif module.params["source_snapshot_label"]:
        snapshot_list = Snapshot.get_snapshots_by_query(
            dict(
                label=module.params["source_snapshot_label"],
                domainUUID=virtual_machine_obj.uuid,
            ),
            rest_client,
        )
    # Check list, raise error if necessary
    check_snapshot_list(module, snapshot_list)
    # Snapshot should be unique at this point
    # Create new key in module.params "hypercore_snapshot_uuid"
    # This key is used in payload function later on.
    module.params["hypercore_snapshot_uuid"] = snapshot_list[0]["snapshot_uuid"]
    return module


def run(module, rest_client):
    # Check if clone with target name already exists.
    if VM.get(query={"name": module.params["vm_name"]}, rest_client=rest_client):
        return (
            False,
            f"Virtual machine {module.params['vm_name']} already exists.",
        )

    # Get Source VM, fail if not found.
    virtual_machine_obj = VM.get_or_fail(
        query={"name": module.params["source_vm_name"]}, rest_client=rest_client
    )[0]

    if module.params["source_snapshot_label"] or module.params["source_snapshot_uuid"]:
        module = get_snapshot(module, rest_client, virtual_machine_obj)

    # Clone and wait for task to finish.
    task = virtual_machine_obj.clone_vm(rest_client, module.params)
    TaskTag.wait_task(rest_client, task)
    task_status = TaskTag.get_task_status(rest_client, task)
    if task_status and task_status.get("state", "") == "COMPLETE":
        return (
            True,
            f"Virtual machine - {module.params['source_vm_name']} - cloning complete to - {module.params['vm_name']}.",
        )
    raise errors.ScaleComputingError(
        f"There was a problem during cloning of {module.params['source_vm_name']}, cloning failed."
    )


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            source_vm_name=dict(
                type="str",
                required=True,
            ),
            tags=dict(  # We give user a chance to add aditional tags here.
                type="list", elements="str"
            ),
            cloud_init=dict(
                type="dict",
                default={},
                options=dict(
                    user_data=dict(type="str"),
                    meta_data=dict(type="str"),
                ),
            ),
            preserve_mac_address=dict(
                type="bool",
                default=False,
                required=False,
            ),
            source_snapshot_label=dict(
                type="str",
            ),
            source_snapshot_uuid=dict(
                type="str",
            ),
        ),
        mutually_exclusive=[("source_snapshot_label", "source_snapshot_uuid")],
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client=client)
        changed, msg = run(module, rest_client)
        module.exit_json(changed=changed, msg=msg)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
