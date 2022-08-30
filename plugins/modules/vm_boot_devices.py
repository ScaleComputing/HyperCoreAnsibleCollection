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
            C(type==scsi_disk), C(type==ide_floppy) or C(type==nvram) it's required to specify.
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
    - Ordered list of boot devices uuid-s, which may be found on /rest/v1/VirDomain
  returned: success
  type: dict
  sample:
    boot_devices:
      - 74df5b47-c468-4626-a7e4-34eca13b2f81
      - a5136b8d-6ef3-4705-95bb-a9567925e4f7
      - b54bba24-7257-421e-83a9-608010cf7a8d
"""

from ansible.module_utils.basic import AnsibleModule
from copy import deepcopy

from ..module_utils import arguments
from ..module_utils.errors import ScaleComputingError
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.utils import filter_dict, transform_query
from ..module_utils.task_tag import TaskTag
from ..module_utils.nic import Nic
from ..module_utils.disk import Disk


SOURCE_OBJECT_QUERY_MAPPING = dict(
    disk_slot="disk_slot", nic_vlan="vlan", iso_name="name"
)


def get_vm_and_boot_devices(module, rest_client):
    vm = VM.get_by_name(module.params, rest_client, must_exist=True)
    boot_devices = vm.boot_devices
    source_objects_ansible = get_source_object_list(rest_client, boot_devices)
    return vm, boot_devices, source_objects_ansible


def get_source_object_query(desired_source_object):
    source_object_raw_query = filter_dict(
        desired_source_object, "disk_slot", "nic_vlan", "iso_name"
    )
    return transform_query(source_object_raw_query, SOURCE_OBJECT_QUERY_MAPPING)


def get_vm_device(vm, desired_source_object):
    source_object_query = get_source_object_query(desired_source_object)
    if desired_source_object["type"] == "nic":  # Retrieve Nic object
        return vm.get_specific_nic(source_object_query)
    source_object_query["type"] = desired_source_object["type"]
    return vm.get_specific_disk(source_object_query)  # Retrieve disk object


def _get_source_object_from_uuid(rest_client, source_object_uuid):
    disk_hypercore_dict = rest_client.get_record(
        "{0}/{1}".format("/rest/v1/VirDomainBlockDevice", source_object_uuid)
    )
    if disk_hypercore_dict:
        return Disk.from_hypercore(disk_hypercore_dict).to_ansible()
    nic_hypercore_dict = rest_client.get_record(
        "{0}/{1}".format("/rest/v1/VirDomainNetDevice", source_object_uuid)
    )
    return Nic.from_hypercore(nic_hypercore_dict).to_ansible()


def get_source_object_list(rest_client, boot_order_list):
    return [
        _get_source_object_from_uuid(rest_client, source_object_uuid)
        for source_object_uuid in boot_order_list
    ]


def update_boot_device_order(module, rest_client, uuid, boot_order):
    # uuid is vm's uuid. boot_order is the desired order we want to set to boot devices
    task_tag = rest_client.update_record(
        "{0}/{1}".format("/rest/v1/VirDomain", uuid),
        dict(bootDevices=boot_order, uuid=uuid),
        module.check_mode,
    )
    TaskTag.wait_task(rest_client, task_tag)


def ensure_absent(module, rest_client):
    vm_before, boot_devices_before, before = get_vm_and_boot_devices(
        module, rest_client
    )
    changed = False
    for desired_boot_device in module.params["items"]:
        vm_device = get_vm_device(vm_before, desired_boot_device)
        if not vm_device or vm_device["uuid"] not in boot_devices_before:
            continue
        uuid = vm_device["uuid"]
        boot_order = deepcopy(boot_devices_before)
        boot_order.remove(uuid)
        update_boot_device_order(module, rest_client, vm_before.uuid, boot_order)
        changed = True
    vm_after, boot_devices_after, after = get_vm_and_boot_devices(module, rest_client)
    return changed, after, dict(before=before, after=after)


def ensure_present(module, rest_client):
    vm_before, boot_devices_before, before = get_vm_and_boot_devices(
        module, rest_client
    )
    changed = False
    for desired_boot_device in module.params["items"]:
        vm_device = get_vm_device(vm_before, desired_boot_device)
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
        update_boot_device_order(
            module, rest_client, vm_before.uuid, desired_boot_order
        )
        changed = True
    vm_after, boot_devices_after, after = get_vm_and_boot_devices(module, rest_client)
    return changed, after, dict(before=before, after=after)


def ensure_set(module, rest_client):
    vm_before, boot_devices_before, before = get_vm_and_boot_devices(
        module, rest_client
    )
    changed = False
    boot_order = []
    for desired_boot_device in module.params["items"]:
        vm_device = get_vm_device(vm_before, desired_boot_device)
        if not vm_device:
            continue
        boot_order.append(vm_device["uuid"])
    if boot_order != boot_devices_before:
        update_boot_device_order(module, rest_client, vm_before.uuid, boot_order)
        changed = True
    vm_after, boot_devices_after, after = get_vm_and_boot_devices(module, rest_client)
    return changed, after, dict(before=before, after=after)


def run(module, rest_client):
    if module.params["state"] == "absent":
        return ensure_absent(module, rest_client)
    elif module.params["state"] == "set":
        return ensure_set(module, rest_client)
    return ensure_present(module, rest_client)


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
            first=dict(
                type="bool",
                default=False,
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
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
