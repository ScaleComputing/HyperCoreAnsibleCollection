#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


# language=yaml
DOCUMENTATION = r"""
module: vm_boot_devices

author:
  - Tjaž Eržen (@tjazsch)
short_description: Manage HyperCore VM's boot devices
description:
  - Use this module to reconfigure VM boot devices.
  - VM boot devices can be set exactly to provided list, or provided list can be inserted before or after current VM boot devices.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
  - scale_computing.hypercore.force_reboot
seealso: []
options:
  state:
    description:
      - The desired state of the boot devices specified by C(items).
      - If I(state=present) devices specified by C(items) will be added to list of boot devices.
      - If I(state=absent) devices specified by C(items) will be removed from the list of boot devices.
      - If I(state=set) VM boot devices will be set exactly to devices specified by C(items).
    choices: [ present, absent, set ]
    type: str
    required: true
  first:
    description:
      - Only relevant if I(state=present).
      - If you want to assign the device the first order, set the value of C(first) to C(1).
    type: bool
    default: false
  items:
    description:
      - The boot devices items we want to change.
    type: list
    elements: dict
    default: []
    suboptions:
      type:
        type: str
        description:
          - The type of device we want to set the boot order to.
          - If setting the boot order for NIC, I(type) should be equal to C(nic).
          - If setting the boot order for disk, I(type) should be equal to one of the specific disk types, listed below.
        choices: [ nic, ide_cdrom, virtio_disk, ide_disk, scsi_disk, ide_floppy, nvram ]
        required: true
      disk_slot:
        type: int
        description:
          - If setting the boot device order of disk, that is I(type=virtio_disk), I(type=ide_disk),
            I(type=scsi_disk), I(type=ide_floppy) or I(type=nvram) disk slot is required to be specified.
          - If setting the boot device order of CD-ROM, that is I(type=ide_cdrom), at least one of I(iso_name)
            or I(disk_slot) is required.
          - If I(type=nic), disk_slot is not relevant.
          - At least one of I(disk_slot), I(nic_vlan) and C(iso_name) is required to identify the VM device to which
            we're setting the boot order.
      nic_vlan:
        type: int
        description:
          - NIC's vlan.
          - If I(type=nic), I(nic_vlan) is required.
          - Otherwise, I(nic_vlan) is not relevant.
          - At least one of I(disk_slot), I(nic_vlan) or I(iso_name) is required to identify the VM device to which
            we're setting the boot order.
      iso_name:
        type: str
        description:
          - The name of ISO image that CD-ROM device is attached to.
          - Only relevant if I(type=ide_cdrom). If I(type=cdrom), at least one of I(iso_name) or I(disk_slot) is
            required to identify CD-ROM device.
          - Otherwise, I(iso_name) is not relevant.
          - At least one of I(disk_slot), I(nic_vlan) and I(iso_name) is required to identify the VM device to which
            we're setting the boot order.
notes:
  - C(check_mode) is not supported.
"""

# language=yaml
EXAMPLES = r"""
- name: Set exact boot order
  scale_computing.hypercore.vm_boot_devices:
    vm_name: name-of-desired-vm
    items:
      - type: virtio_disk
        disk_slot: 2
      - type: nic
        nic_vlan: 10
    state: set
  register: result

- name: Set device as bootable
  scale_computing.hypercore.vm_boot_devices:
    vm_name: name-of-desired-vm
    items:
      - type: nic
        nic_vlan: 2
    state: present
  register: result

- name: Set device as not bootable
  scale_computing.hypercore.vm_boot_devices:
    vm_name: name-of-desired-vm
    items:
      - type: nic
        nic_vlan: 10
    state: absent
  register: result

- name: Set device as first boot device
  scale_computing.hypercore.vm_boot_devices:
    vm_name: name-of-desired-vm
    force_reboot: true
    shutdown_timeout: "{{ '5minutes' | community.general.to_time_unit('seconds') }}"
    items:
      - type: virtio_disk
        disk_slot: 2
      - type: nic
        nic_vlan: 5
    state: present
    first: true
  register: result

- name: Set ISO as first boot device. Identifying CD-ROM by field iso_name
  scale_computing.hypercore.vm_boot_devices:
    vm_name: name-of-desired-vm
    items:
      - type: ide_cdrom
        iso_name: TinyCore-current.iso  # name of ISO image, but it can be used only if ISO is inside CD-ROM
    state: present
    first: true
  register: result

- name: Set ISO as first boot device. Identifying CD-ROM by field disk_slot
  scale_computing.hypercore.vm_boot_devices:
    vm_name: name-of-desired-vm
    items:
      - type: ide_cdrom
        disk_slot: 2
    state: present
    first: true
  register: result
"""

# language=yaml
RETURN = r"""
record:
  description:
    - VM's device that we're assigning the boot order to, which can be either disks from the API endpoint C(/VirDomainBlockDevices),
      or nics from the API endpoint C(/VirDomainNetDevices).
  returned: success
  type: dict
  contains:
    cache_mode:
      description: The cache mode the block device will use
      type: str
      sample: writeback
    disable_snapshotting:
      description: Disables the ability to snapshot the drive
      type: bool
      sample: false
    disk_slot:
      description: Virtual slot the drive will occupy
      type: int
      sample: 2
    mount_points:
      description: Mount points of the drive in the guest OS, populated by the guest-agent
      type: list
      elements: str
      sample: /boot
    iso_name:
      description: Name of the virtual storage device
      type: str
      sample: jc1-disk-0
    read_only:
      description: When true, this device was created via VirDomainSnapshotBlockDeviceCreate with VirDomainSnapshotBlockDeviceCreateOptions
      type: bool
      sample: false
    size:
      description: Logical size of the device in bytes, and can be increased on update or clone
      type: int
      sample: 10737418240
    tiering_priority_factor:
      description: SSD tiering priority factor for block placement
      type: int
      sample: 8
    type:
      description: The bus type the block device will use
      type: str
      sample: virtio_disk
    uuid:
      description: Unique Identifier
      type: str
      sample: d48847d0-91b1-4edf-ab28-3be864494711
    vm_uuid:
      description: Identifier of the VirDomain this device is attached to
      type: str
      sample: 183c5d7c-1e2e-4871-84e8-9ef35bfda5ca
vm_rebooted:
  description:
      - Info if reboot of the VM was performed.
  returned: success
  type: bool
  sample: true
"""

from ansible.module_utils.basic import AnsibleModule
from copy import deepcopy

from ..module_utils import arguments
from ..module_utils.errors import ScaleComputingError
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM


def ensure_absent(module, rest_client):
    vm_before, boot_devices_before, before = VM.get_vm_and_boot_devices(
        module.params, rest_client
    )
    changed = False
    for desired_boot_device in module.params["items"]:
        vm_device = vm_before.get_vm_device(desired_boot_device)
        if not vm_device or vm_device["uuid"] not in boot_devices_before:
            continue
        uuid = vm_device["uuid"]
        boot_order = deepcopy(boot_devices_before)
        boot_order.remove(uuid)
        VM.update_boot_device_order(module, rest_client, vm_before, boot_order)
        changed = True
    vm_after, boot_devices_after, after = VM.get_vm_and_boot_devices(
        module.params, rest_client
    )
    return changed, after, dict(before=before, after=after), vm_before.was_vm_rebooted()


def ensure_present(module, rest_client):
    vm_before, boot_devices_before, before = VM.get_vm_and_boot_devices(
        module.params, rest_client
    )
    changed = False
    for desired_boot_device in module.params["items"]:
        vm_device = vm_before.get_vm_device(desired_boot_device)
        if not vm_device:
            continue
        uuid = vm_device["uuid"]
        if module.params["first"]:
            if uuid in boot_devices_before:
                boot_devices_before.remove(uuid)
            desired_boot_order = [uuid] + boot_devices_before
        else:
            if uuid in boot_devices_before:
                desired_boot_order = boot_devices_before
            else:
                desired_boot_order = boot_devices_before + [uuid]
        if desired_boot_order == boot_devices_before:
            continue
        VM.update_boot_device_order(module, rest_client, vm_before, desired_boot_order)
        changed = True
    vm_after, boot_devices_after, after = VM.get_vm_and_boot_devices(
        module.params, rest_client
    )
    return changed, after, dict(before=before, after=after), vm_before.was_vm_rebooted()


def ensure_set(module, rest_client):
    vm_before, boot_devices_before, before = VM.get_vm_and_boot_devices(
        module.params, rest_client
    )
    changed = vm_before.set_boot_devices(
        module.params["items"], module, rest_client, boot_devices_before
    )
    vm_after, boot_devices_after, after = VM.get_vm_and_boot_devices(
        module.params, rest_client
    )
    return changed, after, dict(before=before, after=after), vm_before.was_vm_rebooted()


def run(module, rest_client):
    vm, boot_devices_before, before = VM.get_vm_and_boot_devices(
        module.params, rest_client
    )
    if module.params["state"] == "absent":
        changed, after, diff, reboot = ensure_absent(module, rest_client)
    elif module.params["state"] == "set":
        changed, after, diff, reboot = ensure_set(module, rest_client)
    else:
        changed, after, diff, reboot = ensure_present(module, rest_client)
    if vm:
        # TODO BUG, this does not work - copy of `vm` is used in say ensure_present
        vm.vm_power_up(module, rest_client)
    return changed, after, diff, reboot


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
            first=dict(
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
                    type=dict(
                        type="str",
                        choices=[
                            "nic",
                            "ide_cdrom",
                            "virtio_disk",
                            "ide_disk",
                            "scsi_disk",
                            "ide_floppy",
                            "nvram",
                        ],
                        required=True,
                    ),
                    disk_slot=dict(
                        type="int",
                    ),
                    nic_vlan=dict(
                        type="int",
                    ),
                    iso_name=dict(
                        type="str",
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
