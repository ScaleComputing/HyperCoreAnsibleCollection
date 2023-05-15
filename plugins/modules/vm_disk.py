#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_disk

author:
  - Tjaž Eržen (@tjazsch)
short_description: Manage VM's disks
description:
  Use this module to add, delete or set disks to the VM.
  The module can also remove all disks from a VM,
  attach and/or detach ISO image to the VM by ISO's name,
  detach ISO image from the VM by disk's disk slot,
  or update the existing disks (disk size etc.).

  For a given VM, a particular disk is selected by combination of (I(type), I(disk_slot)).
  I(disk_slot) means slot on bus (IDE, virtio or SCSI bus).

  Changing disk I(type) can change its I(disk_slot).
  For example, VM has one IDE CD-ROM and one virtio_disk.
  The disk will have C(type=virtio_disk) and C(disk_slot=0),
  and CD-ROM will have C(type=ide_cdrom) and C(disk_slot=0).
  Changing disk I(type) to C(ide_disk) will as place disk on IDE bus,
  after the CD-ROM, and disk will get C(disk_slot=1).

version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
  - scale_computing.hypercore.force_reboot
seealso: []
options:
  force:
    description:
      - A safeguard to prevent unintentional removal of all disks.
      - To remove all disks, items should be set to I(items=[]) and state should be I(state=set) (see example below).
      - In addition, the I(force=true) must be provided.
    type: bool
    default: false
  state:
    description:
      - The desired state of the disks specified by I(items).
      - With I(state=present) (or I(state=absent)), the disks in I(items) are added to VM, or removed from VM.
        Individual disk is resized if needed.
      - With I(state=set), the VM is reconfigured to have exactly such disks as specified by I(items).
    choices: [ present, absent, set ]
    type: str
    required: true
  items:
    description:
      - The disk items we want to change.
    type: list
    elements: dict
    default: []
    suboptions:
      disk_slot:
        type: int
        description:
          - Virtual slot the drive will occupy.
        required: true
      size:
        type: int
        description:
          - Logical size of the device in bytes. I(size) is used for resizing or creating the disk.
          - Will get ignored if performing operations on CD-ROM - C(type=ide_cdrom).
      type:
        type: str
        description:
          - The bus type the VirDomainBlockDevice will use.
          - If I(type=ide_cdrom), I(iso_name) is also required. Se documentation of I(iso_name) for more details.
        choices: [ ide_cdrom, virtio_disk, ide_disk, scsi_disk, ide_floppy, nvram ]
        required: true
      iso_name:
        type: str
        description:
          - The name of ISO image we want to attach/detach from existing VM.
          - In case of attaching ISO image (see example below), I(iso_name) is required. If creating an empty CD-ROM
            but not mount anything, set the value of I(iso_name) to empty string.
          - In case of detaching ISO image (see example below), name is optional. If not specified,
            ISO image present on the C(ide_cdrom) disk will get removed.
      cache_mode:
        type: str
        description:
          - The cache mode the VM will use.
        choices: [ none, writeback, writethrough ]
      disable_snapshotting:
        type: bool
        description:
          - Disables the ability to snapshot the drive.
      tiering_priority_factor:
        type: int
        description:
          - SSD tiering priority factor for block placement.
          - Check the tiering documentation for best practices when modifying this.
          - tiering_priority_factor won't be relevant on cluster that only has a
            single tier - ie. only spinning disk or all flash.
        choices: [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ]
        default: 4
      type_new:
        type: str
        description:
          - Only relevant if we want to update the disk parameters.
          - The type we want to assign the disk with.
notes:
  - C(check_mode) is not supported.
"""


EXAMPLES = r"""
- name: Set exact disk
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    force_reboot: true
    shutdown_timeout: "{{ '5minutes' | community.general.to_time_unit('seconds') }}"
    items:
      - disk_slot: 0
        type: virtio_disk
        size: "{{ '10.1 GB' | human_to_bytes }}"
    state: set

- name: Remove all disks
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items: []
    state: set
    force: true

- name: Remove one disk
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - disk_slot: 0
        type: virtio_disk
    state: absent

- name: Example add/update one disk.
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - disk_slot: 0
        type: virtio_disk
        size: "{{ '10.1 GB' | human_to_bytes }}"
    state: present

- name: Add an empty CD-ROM.
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - disk_slot: 0
        type: ide_cdrom
        iso_name: ""
    state: present

- name: Remove empty CD-ROM.
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - disk_slot: 0
        type: ide_cdrom
    state: absent

- name: Attach existing ISO image to existing VM
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - name: CentOS-Stream-9-latest-x86_64-dvd1.iso
        disk_slot: 0
        type: ide_cdrom
    state: present

- name: Detach ISO image from cdrom disk on slot 0
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - name: CentOS-Stream-9-latest-x86_64-dvd1.iso
        disk_slot: 0
        type: ide_cdrom
    state: absent

- name: Detach ISO image from existing VM, find CD-ROM by slot number and type
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - disk_slot: 0
        type: ide_cdrom
    state: absent

- name: Update existing disk - resize, change type etc
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - disk_slot: 0
        type: ide_disk
        type_new: virtio_disk
        size: "{{ '11.1 GB' | human_to_bytes }}"
        cache_mode: writeback
    state: present

- name: Resize disk
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
    items:
      - disk_slot: 0
        type: virtio_disk
        size: "{{ '20 GB' | human_to_bytes }}"
    state: present
"""


RETURN = r"""
record:
  description:
    - The modified record from the HyperCore API endpoint C(/rest/v1/VirDomainBlockDevice).
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
      sample: virtio_disk
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
      sample: jc1-disk-0
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
from ..module_utils.vm import ManageVMDisks
from ..module_utils.task_tag import TaskTag
from ..module_utils.disk import Disk
from ..module_utils.iso import ISO
from ..module_utils.utils import filter_dict


MODULE_PATH = "scale_computing.hypercore.vm_disk"


def ensure_absent(module, rest_client):
    changed = False
    vm_before, disks_before = ManageVMDisks.get_vm_by_name(module, rest_client)
    for ansible_desired_disk in module.params["items"]:
        disk_query = filter_dict(ansible_desired_disk, "disk_slot", "type")
        ansible_existing_disk = vm_before.get_specific_disk(disk_query)
        if not ansible_existing_disk:
            # No disk - absent is already ensured.
            continue
        existing_disk = Disk.from_ansible(ansible_existing_disk)
        uuid = existing_disk.uuid
        if ansible_desired_disk["type"] == "ide_cdrom":
            # Detach ISO image and don't delete the disk
            name = ""
            if ansible_desired_disk.get("iso_name", None):
                name = ansible_desired_disk["iso_name"]
            elif existing_disk.name:
                name = existing_disk.name
            if name:
                # Detach the ISO image
                iso = ISO.get_by_name(dict(name=name), rest_client, must_exist=True)
                ManageVMDisks.iso_image_management(
                    module, rest_client, iso, uuid, attach=False
                )
        # Remove the disk
        if existing_disk.needs_reboot("delete"):
            vm_before.do_shutdown_steps(module, rest_client)
        task_tag = rest_client.delete_record(
            "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", uuid),
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag, module.check_mode)
        changed = True
    vm_after, disks_after = ManageVMDisks.get_vm_by_name(module, rest_client)
    return (
        changed,
        disks_after,
        dict(before=disks_before, after=disks_after),
        vm_before.reboot,
    )


def run(module, rest_client):
    # ensure_absent is located in modules/vm_disk.py, since it's only used here
    # ensure_present_or_set is located in module_utils/vm.py, since it's also used in module vm.
    vm, disks = ManageVMDisks.get_vm_by_name(module, rest_client)
    if module.params["state"] == "absent":
        changed, records, diff, reboot = ensure_absent(module, rest_client)
    else:
        changed, records, diff, reboot = ManageVMDisks.ensure_present_or_set(
            module, rest_client, MODULE_PATH
        )
    if vm:
        vm.vm_power_up(module, rest_client)
    return changed, records, diff, reboot


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            state=dict(
                type="str",
                choices=["present", "absent", "set"],
                required=True,
            ),
            force=dict(
                type="bool",
                default=False,
            ),
            force_reboot=dict(
                type="bool",
                default=False,
            ),
            shutdown_timeout=dict(
                type="float",
                default=300,
            ),
            items=dict(
                type="list",
                elements="dict",
                default=[],
                options=dict(
                    disk_slot=dict(
                        type="int",
                        required=True,
                    ),
                    size=dict(
                        type="int",
                    ),
                    type=dict(
                        type="str",
                        choices=[
                            "ide_cdrom",
                            "virtio_disk",
                            "ide_disk",
                            "scsi_disk",
                            "ide_floppy",
                            "nvram",
                        ],
                        required=True,
                    ),
                    iso_name=dict(
                        type="str",
                    ),
                    cache_mode=dict(
                        type="str",
                        choices=["none", "writeback", "writethrough"],
                    ),
                    disable_snapshotting=dict(
                        type="bool",
                    ),
                    type_new=dict(
                        type="str",
                    ),
                    tiering_priority_factor=dict(
                        type="int",
                        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                        default=4,
                    ),
                ),
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record, diff, reboot = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff, vm_rebooted=reboot)
    except ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
