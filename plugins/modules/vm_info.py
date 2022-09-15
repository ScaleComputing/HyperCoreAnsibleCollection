#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_info

author:
  - Domen Dobnikar (@domen_dobnikar)
  - Tjaž Eržen (@tjazsch)
short_description: Retrieve information about the VMs.
description:
  - Retrieve information about all or single VM present on the cluster.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  vm_name:
    description:
      - VM's name.
      - Serves as unique identifier across endpoint U(VirDomain).
      - If specified, the VM with that name will get returned. Otherwise, all VMs are going to get returned.
    type: str
"""

EXAMPLES = r"""
- name: Retrieve specific VM
  scale_computing.hypercore.vm_info:
    vm_name: demo-vm
  register: result

- name: Retrieve all VMs.
  scale_computing.hypercore.vm_info:
  register: result
"""

RETURN = r"""
records:
  description:
    - A list of VMs records.
  returned: success
  type: list
  sample:
    vm_name: demo-vm
    description: demo-vm-description
    vcpu: 2
    power_state: stopped
    tags: group-name,tag1,tag2
    uuid: f0c91f97-cbfc-40f8-b918-ab77ae8ea7fb
    boot_devices:
      - cache_mode: none
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
    disks:
      - uuid: e8c8aa6b-1043-48a0-8407-2c432d705378
        vm_uuid: 1596dab1-6f90-494c-9607-b14221830433
        type: virtio_disk
        cache_mode: none
        size: 8100100100
        disk_slot: 0
        name: ""
        disable_snapshotting: false
        tiering_priority_factor: 8
        mount_points: []
        read_only: false
    nics:
      - uuid: 07a2a68a-0afa-4718-9c6f-00a39d08b67e
        vlan: 15
        type: virtio
        mac: 12-34-56-78-AB
        connected: true
        ipv4_addresses: []
    node_affinity:
      strict_affinity: true
      preferred_node:
        backplane_ip: "10.0.0.1"
        lan_ip: "10.0.0.2"
        peer_id: 1
        node_uuid: 638920f2-1069-42ed-b311-5368946f4aca
      backup_node:
        node_uuid: f6v3c6b3-99c6-475b-8e8e-9ae2587db5fc
        backplane_ip: 10.0.0.3
        lan_ip: 10.0.0.4
        peer_id: 2
    snapshot_schedule: demo-snapshot-schedule
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.vm import VM
from ..module_utils.utils import get_query
from ..module_utils.rest_client import RestClient


def run(module, rest_client):
    query = get_query(
        module.params,
        "vm_name",
        ansible_hypercore_map=dict(vm_name="name"),
    )
    return [
        VM.from_hypercore(vm_dict, rest_client).to_ansible()
        for vm_dict in rest_client.list_records("/rest/v1/VirDomain", query)
    ]


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(type="str"),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]
        client = Client(host, username, password)
        rest_client = RestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
