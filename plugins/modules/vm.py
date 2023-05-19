#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm

author:
  - Domen Dobnikar (@domen_dobnikar)
  - Tjaž Eržen (@tjazsch)
short_description: Create, update or delete a VM.
description:
  - Use this module to create, update or delete a VM. When creating or
    updating a VM, setting the disks, network nics and boot order is possible.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
  - scale_computing.hypercore.cloud_init
  - scale_computing.hypercore.force_reboot
seealso:
  - module: scale_computing.hypercore.vm_info
  - module: scale_computing.hypercore.vm_params
  - module: scale_computing.hypercore.vm_boot_devices
  - module: scale_computing.hypercore.vm_disk
  - module: scale_computing.hypercore.vm_nic

  - module: scale_computing.hypercore.vm_node_affinity
  - module: scale_computing.hypercore.vm_replication

  - module: scale_computing.hypercore.vm_clone
  - module: scale_computing.hypercore.vm_import
  - module: scale_computing.hypercore.vm_export
options:
  vm_name_new:
    description:
      - Use it to rename a VM.
      - If the VM already exists, VM's new name.
      - Only relevant if I(state=present).
    type: str
  description:
    description:
      - VM's description.
      - Only relevant if I(state=present).
        value.
    type: str
  memory:
    description:
      - VM's physical memory in bytes.
      - Required if I(state=present). Irrelevant if I(state=absent).
    type: int

  vcpu:
    description:
      - Number of Central processing units on the VM.
      - Required if I(state=present). If I(state=absent), vcpu is not relevant.
    type: int
  power_state:
    description:
      - Desired VM state.
      - States C(PAUSE) and C(LIVEMIGRATE) are not exposed in this module
        (this can be done with raw api module).
      - Note that
        - I(shutdown) will trigger a graceful ACPI shutdown.
        - I(reboot) will trigger a graceful ACPI reboot.
        - I(stop) will trigger an abrupt shutdown (force power off).
          VM might loose data, and filesystem might be corrupted afterwards.
        - I(reset) will trigger an abrupt reset (force power reset).
          VM might loose data, and filesystem might be corrupted afterwards.
    choices: [ start, shutdown, stop, reboot, reset ]
    type: str
    default: start
  snapshot_schedule:
    description:
      - The name of an existing snapshot_schedule to assign to VM.
      - VM can have 0 or 1 snapshot schedules assigned.
    type: str
  state:
    description:
      - Desired state of the VM.
    choices: [ present, absent ]
    type: str
    required: True
  tags:
    description:
      - Tags of the VM.
      - The first tag determines the group that the VM is going to belong.
    type: list
    elements: str
  disks:
    description:
      - List of disks we want to create.
      - Required if I(state=present).
    # default: None
    suboptions:
      disk_slot:
        type: int
        description:
          - Virtual slot the drive will occupy.
        required: true
      size:
        type: int
        description:
          - Logical size of the device in bytes.
      type:
        type: str
        description:
          - The bus type the VM will use.
          - If I(type=ide_cdrom), it's assumed you want to attach ISO image to cdrom disk. In that
            case, field iso_name is required.
        choices: [ ide_cdrom, virtio_disk, ide_disk, scsi_disk, ide_floppy, nvram ]
        required: true
      iso_name:
        type: str
        description:
          - The name of the ISO image we want to attach to the CD-ROM.
          - Required if I(type=ide_cdrom)
          - Only relevant if I(type=ide_cdrom).
      cache_mode:
        type: str
        description:
          - The cache mode the VM will use.
        choices: [ none, writeback, writethrough ]
    type: list
    elements: dict
  nics:
    description:
      - List of network interfaces we want to create.
      - Required if I(state=present).
    type: list
    elements: dict
    # default: None
    suboptions:
      vlan:
        type: int
        default: 0
        description:
          - Network interface virtual LAN.
      mac:
        type: str
        description:
          - Mac address of the network interface.
      type:
        type: str
        default: virtio
        description:
          - Defines type of the network interface.
        choices: [ virtio, RTL8139, INTEL_E1000 ]
      connected:
        type: bool
        default: true
        description:
          - Is network interface connected or not.
  boot_devices:
    description:
      - Ordered list of boot devices (disks and nics) you want to set
    type: list
    elements: dict
    suboptions:
      type:
        type: str
        description:
          - The type of device we want to set the boot order to.
          - If setting the boot order for nic, type should be equal to nic.
          - If setting the boot order for disk, type should be equal to one of
            the specific types, listed below.
        choices: [ nic, ide_cdrom, virtio_disk, ide_disk, scsi_disk, ide_floppy, nvram ]
        required: true
      disk_slot:
        type: int
        description:
          - If setting the boot device order of disk, that is I(type=virtio_disk), I(type=ide_disk),
            I(type=scsi_disk), I(type=ide_floppy) or I(type=nvram) disk_slot is required.
          - If setting the boot device order of CD-ROM, that is I(type=ide_cdrom), at least
            one of I(iso_name) or I(disk_slot) is required.
          - If I(type=nic), disk_slot is not relevant.
          - At least one of I(disk_slot), I(nic_vlan) and I(iso_name) is required to identify
            the VM device to which we're setting the boot order.
      nic_vlan:
        type: int
        description:
          - Nic's vlan.
          - If I(type=nic), I(nic_vlan) is required.
          - Otherwise, I(nic_vlan) is not relevant.
          - At least one of I(disk_slot), I(nic_vlan) and I(iso_name) is required to
            identify the vm device to which we're setting the boot order.
      iso_name:
        type: str
        description:
          - The name of ISO image that CD-ROM device is attached to.
          - Only relevant if I(type=ide_cdrom). If I(type=cdrom), at least one of I(iso_name) or I(disk_slot) is
            required to identify CD-ROM device.
          - Otherwise, I(iso_name) is not relevant.
          - At least one of I(disk_slot), I(nic_vlan) and i(iso_name) is required to identify the vm device to which
            we're setting the boot order.
  attach_guest_tools_iso:
    description:
      - If supported by operating system, create an extra device to attach the Scale Guest OS tools ISO.
      - Supported by I(operating_system=os_windows_server_2012).
    default: false
    type: bool
  operating_system:
    description:
      - Operating system name.
      - Used to select drivers package
    default: os_windows_server_2012
    type: str
    choices: [ os_windows_server_2012, os_other ]
  machine_type:
    description:
      - Scale I(Hardware) version.
      - Required if creating a new VM.
      - Only relevant when creating the VM. This property cannot be modified.
    type: str
    choices: [ BIOS, UEFI, vTPM+UEFI ]
    version_added: 1.1.0
notes:
  - The C(record) return value will be changed from list (containing a single item) to dict.
    There will be no release where both old and new variant work at the same time.
    The change will happen with release 3.0.0.
    To ease migration, the only change between last 1.x or 2.x release and 3.0.0 release
    will be changing the C(record) return value.
    R(List of deprecation changes, scale_computing.hypercore.deprecation)
    includes examples to help with transition.
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Create and start the VM with disks, nics and boot devices set. Attach ISO onto the VM. Add cloud init data
  scale_computing.hypercore.vm:
    vm_name: vm-integration-test-vm
    description: Demo VM
    state: present
    tags:
      - my-group
      - mytag1
      - mytag2
    memory: "{{ '512 MB' | human_to_bytes }}"
    vcpu: 2
    attach_guest_tools_iso: true
    power_state: start
    force_reboot: true
    shutdown_timeout: "{{ '5minutes' | community.general.to_time_unit('seconds') }}"
    disks:
      - type: virtio_disk
        disk_slot: 0
        size: "{{ '10.1 GB' | human_to_bytes }}"
      - type: ide_cdrom
        disk_slot: 0
        iso_name: TinyCore-current.iso
    nics:
      - vlan: 0
        type: RTL8139
    boot_devices:
      - type: virtio_disk
        disk_slot: 0
      - type: nic
        nic_vlan: 0
    cloud_init:
      user_data: "{{ lookup('file', 'cloud-init-user-data-example.yml') }}"
      meta_data: |
        # Content for cloud-init meta-data (or user-data) can be inline too.
  register: result

- name: Delete the VM
  scale_computing.hypercore.vm:
    vm_name: demo-VM
    state: absent
  register: result
"""

RETURN = r"""
record:
  description:
    - Created VM, if creating the record. If deleting the record, none is returned.
  returned: success
  type: list
  elements: dict
  contains:
    vm_name:
      description: Human-readable virtual machine name
      type: str
      sample: demo-vm
    description:
      description: Human-readable description
      type: str
      sample: demo-vm-description
    vcpu:
      description: Number of allotted virtual CPUs
      type: int
      sample: 2
    power_state:
      description: VM's power state
      type: str
      sample: stopped
    tags:
      description: User-modifiable words for organizing a group of VMs
      type: str
      sample: group-name,tag1,tag2
    uuid:
      description: Unique identifier
      type: str
      sample: f0c91f97-cbfc-40f8-b918-ab77ae8ea7fb
    boot_devices:
      description: Bootable disks or nics, in the order that they will boot
      type: list
      elements: dict
      sample:
        cache_mode: none
        disable_snapshotting: false
        disk_slot: 2
        mount_points: []
        iso_name: ""
        read_only: false
        size: 10737418240
        tiering_priority_factor: 8
        type: virtio_disk
        uuid: d48847d0-91b1-4edf-ab28-3be864494711
        vm_uuid: 183c5d7c-1e2e-4871-84e8-9ef35bfda5ca
    disks:
      description: Attached virtual block devices
      type: list
      elements: dict
      sample:
        uuid: e8c8aa6b-1043-48a0-8407-2c432d705378
        vm_uuid: 1596dab1-6f90-494c-9607-b14221830433
        type: virtio_disk
        cache_mode: none
        size: 8100100100
        disk_slot: 0
        iso_name: ""
        disable_snapshotting: false
        tiering_priority_factor: 8
        mount_points: []
        read_only: false
    nics:
      description: Attached virtual network devices
      type: list
      elements: dict
      sample:
        uuid: 07a2a68a-0afa-4718-9c6f-00a39d08b67e
        vlan: 15
        type: virtio
        mac: 12-34-56-78-AB
        connected: true
        ipv4_addresses: []
    node_affinity:
      description: VM's node affinity strategy
      type: dict
      sample:
        strict_affinity: true
        preferred_node:
          backplane_ip: 10.0.0.1
          lan_ip: 10.0.0.2
          peer_id: 1
          node_uuid: 638920f2-1069-42ed-b311-5368946f4aca
        backup_node:
          node_uuid: f6v3c6b3-99c6-475b-8e8e-9ae2587db5fc
          backplane_ip: 10.0.0.3
          lan_ip: 10.0.0.4
          peer_id: 2
    snapshot_schedule:
      description: Name identifier of a snapshot schedule for automated snapshots
      type: str
      sample: demo-snapshot-schedule
    replication_source_vm_uuid:
      description: UUID of source VM if this VM is a replicated VM. Empty string is returned if this VM is not replicated.
      type: str
      sample: 64c9b3a1-3eab-4d16-994f-177bed274f84
      version_added: 1.3.0
vm_rebooted:
  description:
      - Info if reboot of the VM was performed.
  returned: success
  type: bool
  sample: true
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import (
    VM,
    ManageVMParams,
    ManageVMDisks,
    ManageVMNics,
)
from ..module_utils.task_tag import TaskTag

MODULE_PATH = "scale_computing.hypercore.vm"


def _set_boot_order(module, rest_client, vm, existing_boot_order):
    if module.params["boot_devices"] is not None:
        # set_boot_devices return bool whether the order has been changed or not
        boot_order_changed = vm.set_boot_devices(
            module.params["boot_devices"],
            module,
            rest_client,
            existing_boot_order,
        )
        return boot_order_changed, vm.reboot
    return False, vm.reboot


def _set_disks(module, rest_client):
    return ManageVMDisks.ensure_present_or_set(module, rest_client, MODULE_PATH)


def _set_nics(module, rest_client):
    return ManageVMNics.ensure_present_or_set(module, rest_client, MODULE_PATH)


def _set_vm_params(module, rest_client, vm):
    changed_params, reboot, diff = ManageVMParams.set_vm_params(module, rest_client, vm)
    return changed_params, reboot


def ensure_present(module, rest_client):
    vm_before = VM.get_by_old_or_new_name(module.params, rest_client)
    reboot = False
    if vm_before:
        before = vm_before.to_ansible()  # for output
        changed_disks, reboot_disk = _set_disks(module, rest_client)
        changed_nics, reboot_nic = _set_nics(module, rest_client)
        existing_boot_order = vm_before.get_boot_device_order()
        changed_order, reboot_boot_order = _set_boot_order(
            module, rest_client, vm_before, existing_boot_order
        )
        # Set vm params
        # ManageVMParams.set_vm_params has to be executed only after setting the boot order,
        # since boot order cannot be set when the vm is running.
        # set_vm_params updates VM's name, description, tags, memory, number of CPU,
        # changed the power state and/or assigns the snapshot schedule to the VM
        changed_params, reboot_params = _set_vm_params(module, rest_client, vm_before)
        changed = any((changed_order, changed_params, changed_disks, changed_nics))
        reboot = any((reboot_disk, reboot_nic, reboot_boot_order, reboot_params))
        name_field = "vm_name_new" if module.params["vm_name_new"] else "vm_name"
    else:
        before = None  # for output
        # Create new VM object
        new_vm = VM.from_ansible(module.params)
        new_vm.check_vm_before_create()
        # Define the payload and create the VM
        payload = new_vm.post_vm_payload(rest_client, module.params)
        task_tag = rest_client.create_record(
            "/rest/v1/VirDomain",
            payload,
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag)
        # Set boot order
        vm_created = VM.get_by_name(module.params, rest_client)
        existing_boot_order = vm_created.get_boot_device_order()
        _set_boot_order(module, rest_client, vm_created, existing_boot_order)
        # Set power state
        if module.params["power_state"] != "shutdown":
            vm_created.update_vm_power_state(
                module, rest_client, module.params["power_state"]
            )
        changed = True
        name_field = "vm_name"
    vm_after = VM.get_by_name(module.params, rest_client, name_field=name_field)
    after = vm_after.to_ansible()
    if reboot and module.params["power_state"] not in ["shutdown", "stop"]:
        vm_after.reboot = reboot
        vm_after.vm_power_up(module, rest_client)
    return changed, [after], dict(before=before, after=after), vm_after.reboot


def run(module, rest_client):
    if module.params["state"] == "absent":
        return ensure_absent(module, rest_client)
    return ensure_present(module, rest_client)


def ensure_absent(module, rest_client):
    reboot = False
    vm = VM.get_by_name(module.params, rest_client)
    if vm:
        if vm.power_state != "shutdown":  # First, shut it off and then delete
            vm.update_vm_power_state(module, rest_client, "stop")
        task_tag = rest_client.delete_record(
            "{0}/{1}".format("/rest/v1/VirDomain", vm.uuid), module.check_mode
        )
        TaskTag.wait_task(rest_client, task_tag)
        output = vm.to_ansible()
        return True, [output], dict(before=output, after=None), reboot
    return False, [], dict(), reboot


def main():
    module = AnsibleModule(
        supports_check_mode=False,  # False ATM
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
            memory=dict(
                type="int",
            ),
            vcpu=dict(
                type="int",
            ),
            power_state=dict(
                type="str",
                choices=[
                    "start",
                    "shutdown",
                    "stop",
                    "reboot",
                    "reset",
                ],
                default="start",
            ),
            state=dict(
                type="str",
                choices=[
                    "present",
                    "absent",
                ],
                required=True,
            ),
            force_reboot=dict(
                type="bool",
                default=False,
            ),
            shutdown_timeout=dict(
                type="float",
                default=300,
            ),
            tags=dict(type="list", elements="str"),
            disks=dict(
                type="list",
                elements="dict",
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
                ),
            ),
            nics=dict(
                type="list",
                elements="dict",
                options=dict(
                    vlan=dict(
                        type="int",
                        default=0,
                    ),
                    connected=dict(
                        type="bool",
                        default=True,
                    ),
                    type=dict(
                        type="str",
                        choices=[
                            "virtio",
                            "RTL8139",
                            "INTEL_E1000",
                        ],
                        default="virtio",
                    ),
                    mac=dict(
                        type="str",
                    ),
                ),
            ),
            boot_devices=dict(
                type="list",
                elements="dict",
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
            attach_guest_tools_iso=dict(type="bool", default=False),
            operating_system=dict(
                type="str",
                choices=["os_windows_server_2012", "os_other"],
                default="os_windows_server_2012",
            ),
            cloud_init=dict(
                type="dict",
                default={},
                options=dict(
                    user_data=dict(type="str"),
                    meta_data=dict(type="str"),
                ),
            ),
            snapshot_schedule=dict(
                type="str",
            ),
            machine_type=dict(type="str", choices=["BIOS", "UEFI", "vTPM+UEFI"]),
        ),
        required_if=[
            (
                "state",
                "present",
                (
                    "memory",
                    "vcpu",
                    "disks",
                    "nics",
                ),
                False,
            ),
        ],
    )

    module.deprecate(
        "The 'record' return value will be changed from list (containing a single item) to dict. "
        "There will be no release where both old and new variant work at the same time. "
        "To ease migration, the only change between last 1.x or 2.x release and 3.0.0 release "
        "will be changing the 'record' return value. "
        "Affected modules are vm and snapshot_schedule.",
        version="3.0.0",
        collection_name="scale_computing.hypercore",
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record, diff, reboot = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff, vm_rebooted=reboot)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
