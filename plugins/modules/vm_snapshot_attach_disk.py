#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


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
options:
  vm_name:
    type: str
    description:
      - Name of the VM we want to attach a VM snapshot disk to.
    required: True
  vm_disk_type:
    type: str
    choices:
      - ide_disk
      - scsi_disk
      - virtio_disk
      - ide_cdrom
      - ide_floppy
      - nvram
      - vtpm
    description:
      - Type of disk on the VM that we want to attach a VM snapshot disk to.
    required: True
  vm_disk_slot:
    type: int
    description:
      - Specify a disk slot from a vm to identify destination disk.
    required: True
  source_snapshot_uuid:
    type: str
    description:
      - UUID of the snapshot we want to use on a VM.
    required: True
  source_disk_type:
    type: str
    choices:
      - ide_disk
      - scsi_disk
      - virtio_disk
      - ide_cdrom
      - ide_floppy
      - nvram
      - vtpm
    description:
      - Specify a disk type from source snapshot.
    required: True
  source_disk_slot:
    type: int
    description:
      - Specify a disk slot from source snapshot to identify source disk.
    required: True
notes:
  - C(check_mode) is not supported
  - The VM to which the user is trying to attach the snapshot disk, B(must not) be running.
"""


EXAMPLES = r"""
- name: Attach a disk from a VM Snapshot to a VM
  scale_computing.hypercore.vm_snapshot_attach_disk:
    vm_name: test-snapshot_attach_disk-ana
    vm_disk_type: virtio_disk
    vm_disk_slot: 19
    source_snapshot_uuid: "116d51cc-ec25-4628-a092-86de42699aac"
    source_disk_type: virtio_disk
    source_disk_slot: 1
"""

RETURN = r"""
record:
  description:
    - Newly attached disk from a VM snapshot to a VM.
  returned: success
  type: dict
  sample:
    allocation: 0
    block_device_uuid: 5b4b7324-eccf-43c9-925a-6417e02860ff
    cache_mode: "NONE"
    capacity: 100000595968
    created_timestamp: 0
    disable_snapshotting: false
    mount_points: []
    name: ""
    path: scribe/5b4b7324-eccf-43c9-925a-6417e02860ff
    physical: 0
    read_only: false
    share_uuid: ""
    slot: 21
    tiering_priority_factor: 8
    type: VIRTIO_DISK
    vm_uuid: e18ec6af-9dd2-41dc-89af-8ce637171524
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm_snapshot import VMSnapshot
from ..module_utils.task_tag import TaskTag
from ..module_utils.typed_classes import TypedDiff
from typing import Tuple, Dict, Any, Optional


# TODO:
#  - [x] fix code for mypy, sanity, etc.
#  - [x] create integration tests for vm_snapshot_attach_disk
#  - [ ] create unit tests for vm_snapshot modules
#     - check if vm_snapshot_info already has unit tests (if not, add them)


# ++++++++++++
# Must be reviewed - not sure if that's how this should work
# ++++++++++++
def attach_disk(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[Dict[Any, Any]], TypedDiff]:
    # =============== SAVE PARAMS VALUES ===============
    # destination
    vm_name = module.params["vm_name"]
    vm_disk_type = module.params["vm_disk_type"].upper()
    vm_disk_slot = int(module.params["vm_disk_slot"])

    # source
    source_snapshot_uuid = module.params["source_snapshot_uuid"]
    source_disk_type = module.params["source_disk_type"].upper()
    source_disk_slot = int(module.params[
        "source_disk_slot"
    ])  # the higher the index, the newer the disk

    # =============== IMPLEMENTATION ===================
    vm_snapshot_hypercore = VMSnapshot.get_snapshot_by_uuid(
        source_snapshot_uuid, rest_client
    )

    # if the desired snapshot (with source_snapshot_uuid) doesn't exist, raise an error.
    if vm_snapshot_hypercore is None:
        raise errors.ScaleComputingError(
            "Snapshot with uuid='" + source_snapshot_uuid + "' doesn't exist."
        )

    vm_snapshot = vm_snapshot_hypercore.to_ansible()

    vm_uuid = VMSnapshot.get_external_vm_uuid(vm_name, rest_client)

    # Check if slot already taken
    # - check if there is already a disk (vm_disk) with type (vm_type) on slot (vm_slot)
    # - if this slot is already taken, return no change
    #   --> should it be an error that tells the user that the slot is already taken instead?
    before_block_device = VMSnapshot.get_vm_disk_info(
        vm_uuid=vm_uuid,
        slot=vm_disk_slot,
        _type=vm_disk_type,
        rest_client=rest_client,
    )
    if before_block_device is not None:
        # changed, after, diff
        return (
            False,
            before_block_device,
            dict(before=before_block_device, after=None),
        )

    source_disk_info = VMSnapshot.get_snapshot_block_device(
        vm_snapshot, slot=source_disk_slot, _type=source_disk_type
    )

    # build a payload according to /rest/v1/VirDomainBlockDevice/{uuid}/clone documentation
    payload = dict(
        options=dict(
            regenerateDiskID=True,  # required
            readOnly=source_disk_info["read_only"],  # required
        ),
        snapUUID=source_snapshot_uuid,
        template=dict(
            virDomainUUID=vm_uuid,  # required
            type=vm_disk_type,  # required
            capacity=source_disk_info["capacity"],  # required
            chacheMode=source_disk_info["cache_mode"],
            slot=vm_disk_slot,
            disableSnapshotting=source_disk_info["disable_snapshotting"],
            tieringPriorityFactor=source_disk_info["tiering_priority_factor"],
        ),
    )

    create_task_tag = rest_client.create_record(
        endpoint="/rest/v1/VirDomainBlockDevice/{0}/clone".format(
            source_disk_info["uuid"]
        ),
        payload=payload,
        check_mode=module.check_mode,
    )

    TaskTag.wait_task(rest_client, create_task_tag)
    created_block_device = VMSnapshot.get_vm_disk_info_by_uuid(
        create_task_tag["createdUUID"], rest_client
    )

    # return changed, after, diff
    return (
        # if new block device was created, then this should not be None
        created_block_device is not None,
        created_block_device,
        dict(
            before=None, after=created_block_device
        ),  # before, we ofcourse, didn't have that new block device, and after we should have it
    )


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[Dict[Any, Any]], TypedDiff]:
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
                choices=[
                    "ide_disk",
                    "scsi_disk",
                    "virtio_disk",
                    "ide_cdrom",
                    "ide_floppy",
                    "nvram",
                    "vtpm",
                ],
                required=True,
            ),
            vm_disk_slot=dict(
                type="int",
                required=True,
            ),
            source_snapshot_uuid=dict(type="str", required=True),
            source_disk_type=dict(
                type="str",
                choices=[
                    "ide_disk",
                    "scsi_disk",
                    "virtio_disk",
                    "ide_cdrom",
                    "ide_floppy",
                    "nvram",
                    "vtpm",
                ],
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
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
