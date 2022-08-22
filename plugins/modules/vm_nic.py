#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_nic

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Plugin handles actions over network interfaces
description:
  - Plugin enables actions over network interfaces on a specified virtual machine
  - Can create, update, delete specified network interfaces
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  state:
    description:
      - State defines which operation should plugin do over selected network interfaces
      - present, absent, set
    choices: [ present, absent, set ]
    type: str
    required: True
  vm_name:
    description:
      - Virtual machine name
      - Used to identify selected virtual machine by name
    type: str
    required: true
  items:
    description:
      - List of network interfaces
    type: list
    elements: dict
"""

EXAMPLES = r"""
- name: Set NIC interface
  scale_computing.hypercore.vm_nic:
    vm_name: XLAB-demo-vm
    items:
      - vlan: 0
        type: RTL8139
    state: set
- name: Remove all nic interfces
  scale_computing.hypercore.vm_nic:
    vm_name: XLAB-demo-vm
    items:
    state: set

- name: Add/Update NICs interface
  scale_computing.hypercore.vm_nic:
    vm_name: XLAB-demo-vm
    items:
      - vlan: 1
        type: virtio
      - vlan: 2
        type: RTL8139
    state: present

- name: Remove one NIC interface
  scale_computing.hypercore.vm_nic:
    vm_name: XLAB-demo-vm
    items:
      - vlan: 1
        type: virtio
    state: absent

- name: Change VLAN on NIC
  scale_computing.hypercore.vm_nic:
    vm_name: XLAB-demo-vm
    items:
      - vlan: 1
        vlan_new: 10
    state: set

- name: Set NIC interfaces on multiple virtual machines
  scale_computing.hypercore.vm_nic:
    vm_name: "{{ item }}"
    items:
      - vlan: 0
        type: RTL8139
    state: present
  loop:
  - XLAB-demo-vm
  - XLAB-POST-TEST
  - XLAB-us11-example6

- name: Change mac on NIC
  scale_computing.hypercore.vm_nic:
    vm_name: XLAB-demo-vm
    items:
      - vlan: 1
        mac_new: 01:23:45:67:89:AB
    state: set
"""

RETURN = r"""
records:
  description:
    - The created or changed record for nic on a specified virtual machine.
  returned: success
  type: list
  sample:
    - uuid: 07a2a68a-0afa-4718-9c6f-00a39d08b67e
      vlan: 15
      type: virtio
      mac: 12-34-56-78-AB
      connected: true
      ipv4_addresses: []
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.nic import Nic
from ..module_utils.state import NicState


def ensure_present_or_set(module, rest_client):
    before = []
    after = []
    changed = False
    virtual_machine_obj_list = VM.get_or_fail(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )
    if module.params["items"]:
        for nic in module.params["items"]:
            nic["vm_uuid"] = virtual_machine_obj_list[0].uuid
            nic = Nic.from_ansible(ansible_data=nic)
            existing_hc3_nic, existing_hc3_nic_with_new = virtual_machine_obj_list[
                0
            ].find_nic(
                vlan=nic.vlan, mac=nic.mac, vlan_new=nic.vlan_new, mac_new=nic.mac_new
            )
            if (
                existing_hc3_nic_with_new
                and existing_hc3_nic_with_new.is_update_needed(nic)
            ):  # Update existing with vlan_new or mac_new - corner case
                changed, before, after = Nic.send_update_nic_request_to_hypercore(
                    rest_client, nic, existing_hc3_nic_with_new, before, after
                )
            elif (
                existing_hc3_nic
                and not existing_hc3_nic_with_new
                and existing_hc3_nic.is_update_needed(nic)
            ):  # Update existing
                changed, before, after = Nic.send_update_nic_request_to_hypercore(
                    rest_client, nic, existing_hc3_nic, before, after
                )
            else:  # Create new
                changed, before, after = Nic.send_create_nic_request_to_hypercore(
                    rest_client=rest_client, new_nic=nic, before=before, after=after
                )
    else:  # empty set in ansible, delete all
        for nic in virtual_machine_obj_list[0].nic_list:
            before.append(nic.to_ansible())
    updated_virtual_machine = VM.get(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )[0]
    if module.params["state"] == NicState.set:
        # Check if any nics need to be deleted from the vm
        if updated_virtual_machine.delete_unused_nics_to_hypercore_vm(
            module.params, rest_client
        ):
            changed = True
    return changed, after, dict(before=before, after=after)


def ensure_absent(module, rest_client):
    before = []
    after = []
    changed = False
    virtual_machine_obj_list = VM.get_or_fail(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )
    if module.params["items"]:
        for nic in module.params["items"]:
            nic["vm_uuid"] = virtual_machine_obj_list[0].uuid
            nic = Nic.from_ansible(ansible_data=nic)
            existing_hc3_nic, existing_hc3_nic_with_new = virtual_machine_obj_list[
                0
            ].find_nic(
                vlan=nic.vlan, mac=nic.mac, vlan_new=nic.vlan_new, mac_new=nic.mac_new
            )
            if existing_hc3_nic:  # Delete nic
                changed, before, after = Nic.send_delete_nic_request_to_hypercore(
                    rest_client=rest_client,
                    nic_to_delete=existing_hc3_nic,
                    before=before,
                    after=after,
                )
    return changed, after, dict(before=before, after=after)


def run(module, rest_client):
    if module.params["state"] in [NicState.present, NicState.set]:
        return ensure_present_or_set(module, rest_client)
    else:
        return ensure_absent(module, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                required=True,
                choices=["present", "absent", "set"],
            ),
            vm_name=dict(
                type="str",
                required=True,
            ),
            items=dict(
                type="list",
                elements="dict",
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        rest_client = RestClient(client=client)
        changed, records, diff = run(module, rest_client)
        module.exit_json(changed=changed, records=records, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
