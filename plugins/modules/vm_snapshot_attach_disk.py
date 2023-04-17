#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from hypercore.plugins.module_utils.task_tag import TaskTag

DOCUMENTATION = r"""
module: vm_snapshot_attach_disk

author:
  - Ana Zobec (@anazobec)
short_description: Attach a disk from a snapshot to a VM on HyperCore API.
description:
  - Use this module to attach a disk from a snapshot to a desired VM on HyperCore API.
  - Specified disk from source snapshot will be cloned. Cloned disk is then attached to the destination VM.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.vm_snapshot_info
options:  # TODO: Change options!
  vm_name:
    type: str
    description:
      - Name of the VM we want to attach a VM snapshot disk to.
    required: False
  vm_disk_type:
    type: str
    description:
      - Type of disk on the VM that we want to attach a VM snapshot disk to.
    required: True
  vm_disk_slot:
    type: int
    description:
      - Specify a disk slot from a vm to identify destination disk.
  source_snapshot_uuid:
    type: str
    description:
      - UUID of the snapshot we want to use on a VM.
    required: True
  source_disk_type:
    type: str
    description:
      - Specify a disk type from source snapshot.
    required: True
  source_disk_slot:
    type: int
    description:
      - Specify a disk slot from source snapshot to identify source disk.
    required: True
"""


EXAMPLES = r"""
- name: Attach a disk from an automated (scheduled) VM Snapshot to VM
  scale_computing.hypercore.vm_snapshot_attach_disk
    source_snapshot_uuid: ec91ce38-a795-4c0b-bc72-60f8ddba8d91
    snapshot_type: automated
    vm_disk_slot: 0
  
- name: Attach a disk from an user-made VM Snapshot to VM
  scale_computing.hypercore.vm_snapshot_attach_disk
    source_snapshot_uuid: ec91ce38-a795-4c0b-bc72-60f8ddba8d91
    snapshot_type: user
    vm_disk_slot: 0
"""

# TODO: return like vm module
#  - will update this, when I implement the first integration tests
#    for this module.
RETURN = r"""
records:
  description:
    - A list of VM Snapshot records.
  returned: success
  type: list
  sample:
    - automated_trigger_timestamp: 0
      block_count_diff_from_serial_number: 2
      label: snap-2
      local_retain_until_timestamp: 0
      remote_retain_until_timestamp: 0
      replication: true
      snapshot_uuid: 28d6ff95-2c31-4a1a-b3d9-47535164d6de
      timestamp: 1679397326
      type: USER
      vm:
        name: snapshot-test-vm-1
        snapshot_serial_number: 3
        uuid: 5e50977c-14ce-450c-8a1a-bf5c0afbcf43
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm_snapshot import VMSnapshot
from ..module_utils.typed_classes import TypedVMSnapshotToAnsible, TypedDiff
from typing import Tuple, Dict, Union


# ++++++++++++
# Must be reviewed - not sure if that's how this should work
# ++++++++++++
def attach_disk(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedVMSnapshotToAnsible, Dict[None, None]], TypedDiff]:
    # =============== SAVE PARAMS VALUES ===============
    # destination
    vm_name = module.params["vm_name"]
    vm_disk_type = module.params["vm_disk_type"].upper()
    vm_disk_slot = module.params["vm_disk_slot"]

    # source
    source_snapshot_uuid = module.params["source_snapshot_uuid"]
    source_disk_type = module.params["source_disk_type"]
    source_disk_slot = module.params[
        "source_disk_slot"
    ]  # the higher the index, the newer the disk

    # =============== IMPLEMENTATION ===================

    vm_snapshot_list = VMSnapshot.get_snapshots_by_query(
        {"uuid": source_snapshot_uuid}, rest_client
    )  # there is only 1 snapshot with the specified uuid.
    if len(vm_snapshot_list) > 0:
        raise errors.ScaleComputingError(
            "There are too many snapshots with the provided UUID. There should be only one."
        )
    vm_snapshot = vm_snapshot_list[0]

    vm_uuid = vm_snapshot["vm"]["uuid"]

    source_disk_uuid = VMSnapshot.get_source_disk_uuid(vm_snapshot, source_disk_slot)
    source_disk_info = VMSnapshot.get_device_snapshot(
        vm_snapshot,
        uuid=source_disk_uuid,
        slot=source_disk_slot,
        type=source_disk_type
    )

    # build a payload according to /rest/v1/VirDomainBlockDevice/{uuid}/clone documentation
    payload = dict(
        options=dict(
            regenerateDiskID=True,
            readOnly=source_disk_info["read_only"],
        ),
        snapUUID=source_snapshot_uuid,
        template=dict(
            virDomainUUID=vm_uuid,
            # type=source_disk_info["type"], # --> omit for now
            chacheMode=source_disk_info["cache_mode"],
            slot=vm_disk_slot,
            disableSnapshotting=source_disk_info["disable_snapshotting"],
            tieringPriorityFactor=source_disk_info["tiering_priority_factor"],
        ),
    )

    create_task_tag = rest_client.create_record(
        endpoint="/rest/v1/VirDomainBlockDevice/{0}/clone".format(
            source_disk_uuid
        ),
        payload=payload,
        check_mode=module.check_mode,
    )

    TaskTag.wait_task(rest_client, create_task_tag)
    created_block_device = VMSnapshot.get_vm_disk_info(create_task_tag["createdUUID"], rest_client)

    # return changed, after, diff
    return (
        created_block_device is not None,  # if new block device was created, then this should not be None
        created_block_device,
        dict(
            before={}, after=created_block_device
        ),  # before, we ofcourse, didn't have that new block device, and after we should have it
    )


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedVMSnapshotToAnsible, Dict[None, None]], TypedDiff]:
    return attach_disk(module, rest_client)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            vm_disk_type=dict(
                type="str",
                choices=["ide_disk", "scsi_disk", "virtio_disk", "ide_cdrom", "ide_floppy", "nvram", "vtpm"],
                required=True,
            ),
            vm_disk_slot=dict(
                type="int",
                required=True,
            ),
            source_snapshot_uuid=dict(type="str", required=True),
            source_disk_type=dict(
                type="str",
                required=True,
            ),
            source_disk_slot=dict(  # see /rest/v1/VirDomainSnapshot -> deviceSnapshots .. list of available snapshotted disks.
                type="int",
                required=True,
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
