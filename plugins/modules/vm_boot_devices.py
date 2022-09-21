#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_boot_devices

author:
  - Tjaž Eržen (@tjazsch)
short_description: Manage HyperCore's boot devices
description:
  - Add or remove list of devices from boot order (add to end of list).
  - Set exact boot order of the devices.
  - Set a specific list of devices as first, but leave everything else as it is.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  vm_name:
    description:
      - The name of the VM that we want to set the boot order to.
    type: str
    required: true
  state:
    description:
      - The desired state of the disk object.
    choices: [ present, absent, set ]
    type: str
    required: true
  first:
    description:
      - Only relevant if C(state=present).
      - If you want to assign the device the first order, set the value of C(first) to C(1).
    type: bool
    default: false
  force_reboot:
    description:
      - Can VM be forced to power off and on.
      - Only used in instances where modifications to the VM require it to be powered off and VM does not responde to a shutdown request.
      - Before this is utilized, a shutdown request is sent.
    type: bool
    default: false
  shutdown_timeout:
    description:
      - How long does ansible controller wait for VMs response to a shutdown request.
      - In minutes.
    type: int
    default: 5
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
          - If setting the boot order for nic, type should be equal to nic.
          - If setting the boot order for disk, type should be equal to one of the specific types, listed below.
        choices: [ nic, ide_cdrom, virtio_disk, ide_disk, scsi_disk, ide_floppy, nvram ]
        required: true
      disk_slot:
        type: int
        description:
          - If setting the boot device order of disk, that is C(type==virtio_disk), C(type==ide_disk),
            C(type==scsi_disk), C(type==ide_floppy) or C(type==nvram) disk slot is required to be specified.
          - If setting the boot device order of CD-ROM, that is C(type==ide_cdrom), at least one of C(iso_name)
            or C(disk_slot) is required.
          - If C(type==nic), disk_slot is not relevant.
          - At least one of C(disk_slot), C(nic_vlan) and C(iso_name) is required to identify the vm device to which
            we're setting the boot order.
      nic_vlan:
        type: int
        description:
          - Nic's vlan.
          - If C(type==nic), C(nic_vlan) is required to specify.
          - Otherwise, C(nic_vlan) is not relevant.
          - At least one of C(disk_slot), C(nic_vlan) and C(iso_name) is required to identify the vm device to which
            we're setting the boot order.
      iso_name:
        type: str
        description:
          - The name of ISO image that CD-ROM device is attached to.
          - Only relevant if C(type==ide_cdrom). If C(type==cdrom), at least one of C(iso_name) or C(disk_slot) is
            required to identify CD-ROM device.
          - Otherwise, C(iso_name) is not relevant.
          - At least one of C(disk_slot), C(nic_vlan) and C(iso_name) is required to identify the vm device to which
            we're setting the boot order.
"""

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
    shutdown_timeout: 10
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

RETURN = r"""
record:
  description:
    - VM's device that we're assigning the boot order to (either disks, from endpoint /VirDomainBlockDevices, or
      nics, from endpoint /VirDomainNetDevices).
  returned: success
  type: dict
  sample:
    cache_mode: none
    disable_snapshotting: false
    disk_slot: 2
    mount_points: []
    name: ""
    read_only: false
    size: 10737418240
    tiering_priority_factor: 8
    type: virtio_disk
    uuid: d48847d0-91b1-4edf-ab28-3be864494711
    vm_uuid: 183c5d7c-1e2e-4871-84e8-9ef35bfda5ca
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
    return changed, after, dict(before=before, after=after), vm_before.reboot


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
    return changed, after, dict(before=before, after=after), vm_before.reboot


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
    return changed, after, dict(before=before, after=after), vm_before.reboot


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
                type="int",
                default=5,
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
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]
        client = Client(host, username, password)
        rest_client = RestClient(client)
        changed, record, diff, reboot = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff, vm_rebooted=reboot)
    except ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
