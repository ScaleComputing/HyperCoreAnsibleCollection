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
short_description: Plugin handles actions over network interfaces.
description:
  - Plugin enables actions over network interfaces on a specified virtual machine.
  - Can create, update, delete specified network interfaces.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  state:
    description:
      - State defines which operation should plugin do over selected network interfaces.
    choices: [ present, absent, set ]
    type: str
    required: True
  vm_name:
    description:
      - Virtual machine name.
      - Used to identify selected virtual machine by name.
    type: str
    required: true
  items:
    description:
      - List of network interfaces.
    type: list
    elements: dict
    suboptions:
      vlan:
        type: int
        default: 0
        description:
          - Network interface virtual LAN.
      vlan_new:
        type: int
        description:
          - Used to swap network interface to a different virtual LAN.
      mac:
        type: str
        description:
          - Mac address of the network interface.
      mac_new:
        type: str
        description:
          - Used to change mac address on the network interface.
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
    items: []
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
from ..module_utils.vm import VM, ManageVMNics
from ..module_utils.nic import Nic
from ..module_utils.state import NicState


MODULE_PATH = "scale_computing.hypercore.vm_nic"


def ensure_absent(module, rest_client):
    before = []
    after = []
    changed = False
    virtual_machine_obj_list = VM.get(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )
    # VM already absent
    if len(virtual_machine_obj_list) == 0:
        return changed, after, dict(before=before, after=after)
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
                (
                    changed,
                    before,
                    after,
                    reboot,
                ) = ManageVMNics.send_delete_nic_request_to_hypercore(
                    virtual_machine_obj_list[0],
                    module,
                    rest_client=rest_client,
                    nic_to_delete=existing_hc3_nic,
                    before=before,
                    after=after,
                )
                if reboot:
                    virtual_machine_obj_list[0].reboot = reboot
    return (
        changed,
        after,
        dict(before=before, after=after),
        virtual_machine_obj_list[0].reboot,
    )


def run(module, rest_client):
    virtual_machine_obj_list = VM.get(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )
    if module.params["state"] in [NicState.present, NicState.set]:
        changed, records, diff, reboot = ManageVMNics.ensure_present_or_set(
            module, rest_client, MODULE_PATH
        )
    else:
        changed, records, diff, reboot = ensure_absent(module, rest_client)
    if virtual_machine_obj_list[0]:
        virtual_machine_obj_list[0].vm_power_up(module, rest_client)
    return changed, records, diff, reboot


def main():
    module = AnsibleModule(
        supports_check_mode=False,
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
                default=[],
                options=dict(
                    vlan=dict(
                        type="int",
                        default=0,
                    ),
                    vlan_new=dict(
                        type="int",
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
                        required=False,
                        default="virtio",
                    ),
                    mac=dict(
                        type="str",
                    ),
                    mac_new=dict(
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
        rest_client = RestClient(client=client)
        changed, records, diff, reboot = run(module, rest_client)
        module.exit_json(
            changed=changed, records=records, diff=diff, vm_rebooted=reboot
        )
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
