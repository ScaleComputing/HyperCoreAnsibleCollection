#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: vm_snapshot_info

author:
  - Ana Zobec (@anazobec)
short_description: List VM snapshots on HyperCore API
description:
  - Use this module to list information about the VM Snapshots on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.vm_snapshot
options:
  vm_name:
    type: str
    description:
      - List snapshots by this desired VM name
    required: False
  label:
    type: str
    description:
      - List snapshots by this desired snapshot label
    required: False
  serial:
    type: int
    description:
      - List snapshots by this desired serial
    required: False
"""


EXAMPLES = r"""
- name: List all VM snapshots on HyperCore API
  scale_computing.hypercore.vm_snapshot_info:
  register: vm_snapshot
  
- name: List all VM snapshots on HyperCore API with label="example-label"
  scale_computing.hypercore.vm_snapshot_info:
    label: example-label
  register: vm_snapshot

- name: List all VM snapshots on HyperCore API with vm_name="example-vm"
  scale_computing.hypercore.vm_snapshot_info:
    vm_name: example-vm
  register: vm_snapshot
  
- name: List all VM snapshots on HyperCore API with serial=0
  scale_computing.hypercore.vm_snapshot_info:
    serial: 0
  register: vm_snapshot
  
- name: >-
    List all VM snapshots on HyperCore API with
    label="example-label", vm_name="example-vm", serial=0
  scale_computing.hypercore.vm_snapshot_info:
    label: example-label
    vm_name: example-vm
    serial: 0
  register: vm_snapshot
"""

RETURN = r"""
records:
  description:
    - A list of VM Snapshot records.
  returned: success
  type: list
  sample:
    - automated_trigger_timestamp: 0
      block_count_diff_from_serial_number: 2
      label: snap-2
      local_retain_until_timestamp: 0
      remote_retain_until_timestamp: 0
      replication: true
      snapshot_uuid: 28d6ff95-2c31-4a1a-b3d9-47535164d6de
      timestamp: 1679397326
      type: USER
      vm:
        name: snapshot-test-vm-1
        snapshot_serial_number: 3
        uuid: 5e50977c-14ce-450c-8a1a-bf5c0afbcf43
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm_snapshot import VMSnapshot
from ..module_utils.typed_classes import TypedVMSnapshotToAnsible
from typing import List, Optional


def run(
    module: AnsibleModule, rest_client: RestClient
) -> List[Optional[TypedVMSnapshotToAnsible]]:
    filtered = VMSnapshot.filter_snapshots_by_params(module.params, rest_client)
    return filtered


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=False,
            ),
            label=dict(type="str", required=False),
            serial=dict(type="int", required=False),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
