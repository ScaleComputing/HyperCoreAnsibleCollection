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
  - Add, delete or set disk to the VM.
  - Force remove all VM's disks.
  - Attach and/or detach ISO image to the VM by iso's name.
  - Detach ISO image from the VM by disk's disk slot.
  - Update existing disk.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  vm_name:
    description:
      - Virtual machine's name.
      - Serves as unique identifier across all snapshot schedules.
    type: str
    required: true
  force:
    description:
      - If set to 1 and C(state==set), all disk interfaces are going to be removed.
      - Additionally, items should be set to C([]) (see example below) when deleting all disks
    type: int
    choices: [ 0, 1 ]
    default: 0
  state:
    description:
      - The desired state of the disk object.
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
          - Logical size of the device in bytes. Below is example of resizing and creating the disk.
          - In case you're creating a disk, size needs to be specified.
      type:
        type: str
        description:
          - The bus type the VirDomainBlockDevice will use.
          - If C(type==ide_cdrom), it's assumed you want to attach ISO image to cdrom disk. In that
            case, field name is required.
        choices: [ ide_cdrom, virtio_disk, ide_disk, scsi_disk, ide_floppy, nvram ]
        required: true
      iso_name:
        type: str
        description:
          - The name of ISO image we want to attach/detach from existing VM.
          - In case of attaching ISO image (see example below), name is required.
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
      type_new:
        type: str
        description:
          - Only relevant if we want to update the disk parameters.
          - The type we want to assign the disk with.
"""


EXAMPLES = r"""
- name: Set exact disk
  scale_computing.hypercore.vm_disk:
    vm_name: demo-vm
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
    force: 1

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
    - The modified record from the HyperCore API on the endpoint /rest/v1/VirDomainBlockDevice.
  returned: success
  type: dict
  sample:
    uuid: 056ea04b-069c-4a22-84d5-5489b100029f
    vm_uuid: 1596dab1-6f90-494c-9607-b14221830433
    type: VIRTIO_DISK
    cache_mode: NONE
    size: 81001000100
    disk_slot: 0
    name: jc1-disk-0
    disable_snapshotting: False
    tiering_priority_factor: 8
    mount_points: []
    read_only: false
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments
from ..module_utils.errors import ScaleComputingError
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.task_tag import TaskTag
from ..module_utils.disk import Disk
from ..module_utils.iso import ISO
from ..module_utils.utils import is_superset, filter_dict


def get_vm_by_name(module, rest_client):
    """
    Wrapps VM's method get_by_name. Additionally, it raises exception if vm isn't found
    Returns vm object and list of ansible disks (this combo is commonly used in this module).
    """
    # If there's no VM with such name, error is raised automatically
    vm = VM.get_by_name(module.params, rest_client, must_exist=True)
    return vm, [disk.to_ansible() for disk in vm.disks]


def create_block_device(module, rest_client, vm, desired_disk):
    # vm is instance of VM, desired_disk is instance of Disk
    payload = desired_disk.post_payload(vm)
    task_tag = rest_client.create_record(
        "/rest/v1/VirDomainBlockDevice",
        payload,
        module.check_mode,
    )
    TaskTag.wait_task(rest_client, task_tag)
    return task_tag["createdUUID"]


def iso_image_management(module, rest_client, iso, uuid, attach):
    # iso is instance of ISO, uuid is uuid of block device
    # Attach is boolean. If true, you're attaching an image.
    # If false, it means you're detaching an image.
    payload = iso.attach_iso_payload() if attach else iso.detach_iso_payload()
    task_tag = rest_client.update_record(
        "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", uuid),
        payload,
        module.check_mode,
    )
    # Not returning anything, since it isn't used in code.
    # Disk's uuid is stored in task_tag if relevant in the future.
    TaskTag.wait_task(rest_client, task_tag)


def force_remove_all_disks(module, rest_client, vm, disks_before):
    # It's important to check if items is equal to empty list and empty list only (no None-s)
    if module.params["items"] != []:
        raise ScaleComputingError(
            "If force set to 1, items should be set to empty list"
        )
    # Delete all disks
    for existing_disk in vm.disks:
        task_tag = rest_client.delete_record(
            "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", existing_disk.uuid),
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag)
    return True, [], dict(before=disks_before, after=[])


def update_block_device(module, rest_client, desired_disk, existing_disk, vm):
    payload = desired_disk.patch_payload(vm, existing_disk)
    task_tag = rest_client.update_record(
        "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", existing_disk.uuid),
        payload,
        module.check_mode,
    )
    TaskTag.wait_task(rest_client, task_tag)


def delete_not_used_disks(module, rest_client, changed):
    updated_vm, updated_ansible_disks = get_vm_by_name(module, rest_client)
    # Ensure all disk that aren't listed in items don't exist in VM (ensure absent)
    for updated_ansible_disk in updated_ansible_disks:
        existing_disk = Disk.from_ansible(updated_ansible_disk)
        to_delete = True
        for ansible_desired_disk in module.params["items"]:
            desired_disk = Disk.from_ansible(ansible_desired_disk)
            if (
                desired_disk.slot == existing_disk.slot
                and desired_disk.type == existing_disk.type
            ):
                to_delete = False
        if to_delete:
            task_tag = rest_client.delete_record(
                "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", existing_disk.uuid),
                module.check_mode,
            )
            TaskTag.wait_task(rest_client, task_tag)
            changed = True
    return changed


def ensure_present_or_set(module, rest_client):
    changed = False
    vm_before, disks_before = get_vm_by_name(module, rest_client)
    if module.params["state"] == "set" and module.params["force"] == 1:
        return force_remove_all_disks(module, rest_client, vm_before, disks_before)
    for ansible_desired_disk in module.params["items"]:
        # For the given VM, disk can be uniquely identified with disk_slot and type or
        # just name, if not empty string
        disk_query = filter_dict(ansible_desired_disk, "disk_slot", "type")
        ansible_existing_disk = vm_before.get_specific_disk(disk_query)
        desired_disk = Disk.from_ansible(ansible_desired_disk)
        if ansible_desired_disk["type"] == "ide_cdrom":
            # ISO image detachment
            # Check if ide_cdrom disk already exists
            if ansible_existing_disk:
                existing_disk = Disk.from_ansible(ansible_existing_disk)
                uuid = existing_disk.uuid
            else:
                # Create new ide_cdrom disk
                uuid = create_block_device(module, rest_client, vm_before, desired_disk)
            # Attach ISO image
            # If ISO image's name is specified, it's assumed you want to attach ISO image
            name = ansible_desired_disk["iso_name"]
            iso = ISO.get_by_name(dict(name=name), rest_client, must_exist=True)
            iso_image_management(module, rest_client, iso, uuid, attach=True)
            changed = True
        else:
            if ansible_existing_disk:
                existing_disk = Disk.from_ansible(ansible_existing_disk)
                # Check superset for idempotency
                ansible_desired_disk_filtered = {
                    k: v for k, v in desired_disk.to_ansible().items() if v is not None
                }
                if is_superset(ansible_existing_disk, ansible_desired_disk_filtered):
                    # There's nothing to do - all properties are already set the way we want them to be
                    continue

                update_block_device(
                    module, rest_client, desired_disk, existing_disk, vm_before
                )
            else:
                create_block_device(module, rest_client, vm_before, desired_disk)
            changed = True
    if module.params["state"] == "set":
        changed = delete_not_used_disks(module, rest_client, changed)
    vm_after, disks_after = get_vm_by_name(module, rest_client)
    return changed, disks_after, dict(before=disks_before, after=disks_after)


def ensure_absent(module, rest_client):
    changed = False
    vm_before, disks_before = get_vm_by_name(module, rest_client)
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
            if ansible_desired_disk.get("iso_name", None):
                name = ansible_desired_disk["iso_name"]
            elif existing_disk.name:
                name = existing_disk.name
            else:
                raise ScaleComputingError("Don't know which ISO image to detach")
            iso = ISO.get_by_name(dict(name=name), rest_client, must_exist=True)
            iso_image_management(module, rest_client, iso, uuid, attach=False)
        else:
            task_tag = rest_client.delete_record(
                "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", uuid),
                module.check_mode,
            )
            TaskTag.wait_task(rest_client, task_tag)
            changed = True

    vm_after, disks_after = get_vm_by_name(module, rest_client)
    return changed, disks_after, dict(before=disks_before, after=disks_after)


def run(module, rest_client):
    if module.params["state"] == "absent":
        return ensure_absent(module, rest_client)
    return ensure_present_or_set(module, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
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
                type="int",
                choices=[0, 1],
                default=0,
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
                    ),
                ),
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]
        client = Client(host, username, password)
        rest_client = RestClient(client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
