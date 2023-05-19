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
short_description: Handles actions over network interfaces
description:
  - Use vm_nics to perform actions over network interfaces (NIC) on a specified virtual machine.
  - Can create, update or delete specified network interfaces.
  - A single NIC can be identified by
    - I(type) and I(vlan), or
    - I(type) and I(mac)
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
  - scale_computing.hypercore.force_reboot
seealso: []
options:
  state:
    description:
      - State defines which operation should plugin do over selected network interfaces.
    choices: [ present, absent, set ]
    type: str
    required: True
  items:
    description:
      - List of network interfaces.
    type: list
    default: []
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
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Set NIC interface
  scale_computing.hypercore.vm_nic:
    vm_name: XLAB-demo-vm
    force_reboot: true
    shutdown_timeout: "{{ '5minutes' | community.general.to_time_unit('seconds') }}"
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
  elements: dict
  contains:
    uuid:
      description: Unique identifier
      type: str
      sample: 07a2a68a-0afa-4718-9c6f-00a39d08b67e
    vlan:
      description: VLAN tag of the interface
      type: int
      sample: 15
    type:
      description: Virtualized network device types
      type: str
      sample: virtio
    mac:
      description: MAC address of the virtual network device
      type: str
      sample: 12-34-56-78-AB
    connected:
      description: Enabled and can make connections
      type: bool
      sample: true
    ipv4_addresses:
      description: IPv4 addresses registered with this device
      type: list
      elements: str
      sample: 192.0.2.1
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
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client=client)
        changed, records, diff, reboot = run(module, rest_client)
        module.exit_json(
            changed=changed,
            records=records,
            diff=diff,
            vm_rebooted=reboot,
        )
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
