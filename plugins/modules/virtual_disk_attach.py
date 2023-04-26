# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: virtual_disk_attach

author:
  - Polona Mihalič (@PolonaM)
short_description: Clones an uploaded virtual disk and attaches it to a virtual machine.
description:
  - Clones an uploaded virtual disk and attaches it to a virtual machine.
  - If selected slot is not empty, selected virtual disk will not be attached.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
seealso:
  - module: scale_computing.hypercore.virtual_disk
  - module: scale_computing.hypercore.virtual_disk_info
  - module: scale_computing.hypercore.vm_disk
options:
  name:
    description:
      - Name of the virtual disk that we want to attach.
      - Used as a unique identifier of an uploaded virtual disk.
    type: str
    required: true
  disk:
    description:
      - The disk that will be created when selected virtual disk is attached to selected virtual machine.
    type: dict
    suboptions:
      type:
        description:
          - The bus type the block device will use.
          - If I(type=ide_cdrom), I(iso_name) is also required. Se documentation of I(iso_name) for more details.
        type: str
        choices: [ virtio_disk, ide_disk, scsi_disk ]
        required: true
      disk_slot:
        description:
          - Virtual slot the drive will occupy.
        type: int
        required: true
      size:
        description:
          - Logical size of the block device in bytes.
          - Should be greater or equal than the size of virtual disk.
            If smaller then capacity of the new block device/disk will automatically be set to the size of source virtual disk.
          - If not set, defaults to size of source virtual disk.
        type: int
      cache_mode:
        description:
          - The cache mode the virtual machine will use.
        type: str
        choices: [ none, writeback, writethrough ]
      disable_snapshotting:
        description:
          - Disables the ability to snapshot the drive.
        type: bool
      tiering_priority_factor:
        description:
          - SSD tiering priority factor for block placement.
          - Check the tiering documentation for best practices when modifying this.
          - Not relevant for cluster that only has a single tier - ie. only spinning disk or all flash.
        type: int
        choices: [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ]
        default: 4
      read_only:
        description:
          - Mount the new block device as read-only.
        type: bool
        default: False
      regenerate_disk_id:
        description:
          - Regenerate the disk ID, e.g. GPT UUID or MBR signature.
        type: bool
        default: True
"""


EXAMPLES = r"""
- name: Clone an uploaded virtual disk and attach it to a virtual machine.
  scale_computing.hypercore.virtual_disk_attach:
    name: foobar.qcow2
    vm_name: my_virtual_machine
    disk:
      type: virtio_disk
      disk_slot: 0
      size: "{{ '11.1 GB' | human_to_bytes }}"
      cache_mode: writethrough
      disable_snapshotting: true
      tiering_priority_factor: 8
      read_only: true
      regenerate_disk_id: false
  register: disk
"""

RETURN = r"""
record:
  description:
    - Created and attached disk or existing disk in C(disk_slot) in case when the slot is already occupied.
  returned: success
  type: dict
  contains:
    uuid:
      description: Unique Identifier
      type: str
      sample: 056ea04b-069c-4a22-84d5-5489b100029f
    vm_uuid:
      description: Identifier of the VirDomain this device is attached to
      type: str
      sample: 1596dab1-6f90-494c-9607-b14221830433
    type:
      description: The bus type the VirDomainBlockDevice will use
      type: str
      sample: ide_cdrom
    cache_mode:
      description: The cache mode the VirDomainBlockDevice will use
      type: str
      sample: none
    size:
      description: Logical size of the device in bytes, and can be increased on update or clone
      type: int
      sample: 81001000100
    disk_slot:
      description: Virtual slot the drive will occupy
      type: int
      sample: 0
    iso_name:
      description: Name of the virtual storage device
      type: str
      sample: cloud-init-08425e56.iso
    disable_snapshotting:
      description: Disables the ability to snapshot the drive
      type: bool
      sample: False
    tiering_priority_factor:
      description: SSD tiering priority factor for block placement
      type: int
      sample: 8
    mount_points:
      description: Mount points of the drive in the guest OS, populated by the guest-agent
      type: list
      elements: str
      sample: []
    read_only:
      description: True if the device is read-only
      type: bool
      sample: false
"""


from ansible.module_utils.basic import AnsibleModule
from typing import Tuple, Optional, Any, Dict

from ..module_utils.typed_classes import TypedDiff, TypedDiskToAnsible
from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.virtual_disk import VirtualDisk
from ..module_utils.disk import Disk
from ..module_utils.task_tag import TaskTag
from ..module_utils.vm import VM
from ..module_utils.hypercore_version import HyperCoreVersion


HYPERCORE_VERSION_REQUIREMENTS = ">=9.2.10"


def is_slot_available(module: AnsibleModule, vm: VM) -> Tuple[bool, Optional[Disk]]:
    for disk in vm.disks:
        if disk.slot == module.params["disk"]["disk_slot"]:
            return False, disk
    return True, None


def create_payload(
    module: AnsibleModule, vm: VM, virtual_disk: VirtualDisk
) -> Dict[Any, Any]:
    payload = {}
    payload["options"] = dict(
        regenerateDiskID=module.params["disk"]["regenerate_disk_id"],
        readOnly=module.params["disk"]["read_only"],
    )
    payload["template"] = Disk.from_ansible(  # type: ignore
        module.params["disk"]
    ).post_and_patch_payload(vm)
    payload["template"].pop("readOnly")
    # get() does not work, since key is always present
    if module.params["disk"]["size"]:
        # if disk.size < virtual_disk.size, the new block device will automatically have capacity = virtual_disk.size
        payload["template"]["capacity"] = module.params["disk"]["size"]
    else:
        # capacity is required parameter in payload
        payload["template"]["capacity"] = virtual_disk.size
    return payload


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[TypedDiskToAnsible], TypedDiff]:
    vm = VM.get_by_name(module.params, rest_client)  # type: ignore
    slot_available, disk = is_slot_available(module, vm)
    if not slot_available:
        return (
            False,
            disk.to_ansible(),  # type: ignore
            dict(before=disk.to_ansible(), after=disk.to_ansible()),  # type: ignore
        )
    virtual_disk = VirtualDisk.get_by_name(
        rest_client, name=module.params["name"], must_exist=True
    )
    payload = create_payload(module, vm, virtual_disk)  # type: ignore
    task_tag = virtual_disk.attach_to_vm(rest_client, payload)  # type: ignore
    TaskTag.wait_task(rest_client, task_tag)
    disk = Disk.get_by_uuid(task_tag["createdUUID"], rest_client, must_exist=True)
    return (
        True,
        disk.to_ansible(),  # type: ignore
        dict(before=None, after=disk.to_ansible()),  # type: ignore
    )


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(type="str", required=True),
            vm_name=dict(type="str", required=True),
            disk=dict(
                type="dict",
                options=dict(
                    type=dict(
                        type="str",
                        choices=[
                            "virtio_disk",
                            "ide_disk",
                            "scsi_disk",
                        ],
                        required=True,
                    ),
                    disk_slot=dict(type="int", required=True),
                    size=dict(type="int"),
                    cache_mode=dict(
                        type="str", choices=["none", "writeback", "writethrough"]
                    ),
                    disable_snapshotting=dict(type="bool"),
                    tiering_priority_factor=dict(
                        type="int",
                        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                        default=4,
                    ),
                    read_only=dict(type="bool", default=False),
                    regenerate_disk_id=dict(type="bool", default=True),
                ),
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        hcversion = HyperCoreVersion(rest_client)
        hcversion.check_version(module, HYPERCORE_VERSION_REQUIREMENTS)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
