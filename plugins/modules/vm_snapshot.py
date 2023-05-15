# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: vm_snapshot

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Handles VM snapshots.
description:
  - Use this module to perform snapshot creation or deletion.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.vm_snapshot_info
options:
  vm_name:
    type: str
    required: true
    description: source VM name.
  label:
    type: str
    description:
      - Snapshot label, used as identificator in combination with vm_name.
      - Must be unique for a specific VM.
  retain_for:
    type: int
    description:
      - How many days does hypercore retain snapshot.
      - Local and remote retention is set by this.
      - Number of days.
      - VM must be powered on during automatic deletion process.
  replication:
    type: bool
    description: When false, will not replicate snapshot to a remote system if replication is configured.
    default: true
  state:
    description:
      - State of the snapshot.
    choices: [ present, absent]
    type: str
    required: True
  uuid:
    type: str
    description:
      - Snapshot uuid, used as identificator.
      - Can be used instead of label.
      - Must be unique.
"""


EXAMPLES = r"""
- name: Create snapshot with label "new" from VM "test-VM"
  scale_computing.hypercore.vm_snapshot:
    vm_name: test-VM
    label: new
    state: present
  register: vm_snapshot

- name: Create snapshot with label "new" from VM "test-VM" that will automatically delete after 30 days
  scale_computing.hypercore.vm_snapshot:
    vm_name: test-VM
    label: new
    retain_for: 30
    state: present
  register: vm_snapshot

- name: Delete snapshot with label "new" made from VM with name "test-VM"
  scale_computing.hypercore.vm_snapshot:
    vm_name: test-VM
    label: new
    state: absent
  register: vm_snapshot
"""

RETURN = r"""
record:
  description:
    - Snapshot record.
  returned: success
  type: dict
  contains:
    automated_trigger_timestamp:
      description: Unix timestamp used when determining which automated snapshots to retain.
      type: int
      sample: 0
    block_count_diff_from_serial_number:
      description: Snapshot serial number of the previous snapshot.
      type: int
      sample: 0
    label:
      description: Snapshot label.
      type: str
      sample: test
    local_retain_until_timestamp:
      description: Snapshot local retention timestamp.
      type: int
      sample: 1682337511
    remote_retain_until_timestamp:
      description: Snapshot remote retention timestamp.
      type: int
      sample: 1682337511
    replication:
      description: Replicaiton.
      type: bool
      sample: true
    snapshot_uuid:
      description: Snapshot unique identifier.
      type: str
      sample: e7dca7ca-aa75-4c9d-a59a-6a27ad823942
    timestamp:
      description: Timestamp of snapshot creation.
      type: str
      sample: 1682337511
    type:
      description: Snapshot type.
      type: str
      sample: USER
    vm:
      description: Virtual machine used in snapshot.
      type: dict
      sample:
        name: test-VD-Domen
        snapshot_serial_number: 23
        uuid: 7c4f0fa5-868c-4d06-89d7-c5db7d142030
"""

from ansible.module_utils.basic import AnsibleModule
from typing import Tuple, Optional, List

from ..module_utils.typed_classes import (
    TypedVMSnapshotToAnsible,
    TypedDiff,
)
from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.utils import is_changed
from ..module_utils.state import State
from ..module_utils.task_tag import TaskTag
from ..module_utils.vm_snapshot import VMSnapshot
from ..module_utils.vm import VM


def get_snapshot(
    module: AnsibleModule, rest_client: RestClient, vm_object: VM
) -> List[TypedVMSnapshotToAnsible]:
    # Get snapshot by uuid first if parameter exists.
    if module.params["uuid"]:
        snapshot_list = [
            VMSnapshot.get_snapshot_by_uuid(  # type: ignore
                module.params["uuid"], rest_client, must_exist=True
            ).to_ansible()
        ]
    # Otherwise get by label
    else:
        snapshot_list = VMSnapshot.get_snapshots_by_query(
            dict(label=module.params["label"], domainUUID=vm_object.uuid), rest_client
        )

    # Snapshot should be unique by this point.
    if len(snapshot_list) > 1:
        raise errors.ScaleComputingError(
            f"Virtual machine - {module.params['vm_name']} - has more than one snapshot with label - {module.params['label']}, specify uuid instead."
        )

    return snapshot_list


def ensure_present(
    module: AnsibleModule,
    rest_client: RestClient,
    vm_object: VM,
    snapshot_list: Optional[List[TypedVMSnapshotToAnsible]],
) -> Tuple[bool, Optional[TypedVMSnapshotToAnsible], TypedDiff]:
    before = snapshot_list[0] if snapshot_list and len(snapshot_list) > 0 else None
    after = None

    # snapshot already exist, do nothing.
    if snapshot_list:
        return False, before, dict(before=before, after=before)

    # Create object and send create request.
    snapshot_ansible_obj = VMSnapshot.from_ansible(module.params)
    snapshot_ansible_obj.domain = vm_object
    task = snapshot_ansible_obj.send_create_request(rest_client)
    TaskTag.wait_task(rest_client, task)

    # Get after from API
    after_list = VMSnapshot.get_snapshots_by_query(
        dict(label=module.params["label"], domainUUID=vm_object.uuid), rest_client
    )
    after = after_list[0] if after_list and len(after_list) > 0 else None
    return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(
    module: AnsibleModule,
    rest_client: RestClient,
    vm_object: VM,
    snapshot_list: Optional[List[TypedVMSnapshotToAnsible]],
) -> Tuple[bool, Optional[TypedVMSnapshotToAnsible], TypedDiff]:
    before = snapshot_list[0] if snapshot_list and len(snapshot_list) > 0 else None
    after = None

    # Snapshot already absent, do nothing.
    if not snapshot_list:
        return False, before, dict(before=before, after=before)

    # Send delete request.
    task = VMSnapshot.send_delete_request(
        rest_client, snapshot_list[0]["snapshot_uuid"]
    )
    TaskTag.wait_task(rest_client, task)

    # Get after from API, check snapshot was deleted.
    after_list = VMSnapshot.get_snapshots_by_query(
        dict(label=module.params["label"], domainUUID=vm_object.uuid), rest_client
    )
    after = after_list[0] if after_list and len(after_list) > 0 else None
    return is_changed(before, after), after, dict(before=before, after=after)


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[TypedVMSnapshotToAnsible], TypedDiff]:
    vm_object: VM = VM.get_by_name(module.params, rest_client, must_exist=True)  # type: ignore
    snapshot_list = get_snapshot(module, rest_client, vm_object)

    if module.params["state"] == State.present:
        return ensure_present(module, rest_client, vm_object, snapshot_list)
    return ensure_absent(module, rest_client, vm_object, snapshot_list)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=[
                    "present",
                    "absent",
                ],
                required=True,
            ),
            vm_name=dict(
                type="str",
                required=True,
            ),
            label=dict(
                type="str",
            ),
            retain_for=dict(
                type="int",
            ),
            replication=dict(
                type="bool",
                default=True,
            ),
            uuid=dict(
                type="str",
            ),
        ),
        mutually_exclusive=[("label", "uuid")],
        required_if=[
            ("state", "absent", ("label", "uuid"), True),
            ("state", "present", ["label"]),
        ],
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
