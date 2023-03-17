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
    label: some-label
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
      block_count_diff_from_serial_number: null
      domain_uuid: 4dd639c7-f153-4c9a-890c-888d85654f1
      label: user-made-snapshot
      local_retain_until_timestamp: 0
      remote_retain_until_timestamp: 0
      replication: true
      timestamp: 1678707134
      type: USER
      uuid: 0d49b516-bad6-44f4-b22b-02fa9423a7da
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm_snapshot import VMSnapshot
from ..module_utils.typed_classes import TypedVMSnapshotToAnsible
from typing import List, Optional, Dict, Any


def build_query(params: Optional[Dict[Any, Any]]):
    query = {}
    if params["label"]:
        query["label"] = params["label"]
    if params["serial"]:
        query["domain.snapshotSerialNumber"] = params["serial"]
    if params["vm_name"]:
        query["domain.name"] = params["vm_name"]

    return query


def run(
    module: AnsibleModule, rest_client: RestClient
) -> List[Optional[TypedVMSnapshotToAnsible]]:
    all_vm_snapshots = VMSnapshot.get_snapshots_by_query({}, rest_client)

    query = build_query(module.params)
    if query == {}:
        return all_vm_snapshots

    # else filter results by label, domain.name, domain.snapshotSerialNumber
    # ++++++++++++++++++ NOTE
    # --> This "ugly" filtering had to be done, because method list_records doesn't support nested queries
    #     it's the best solution I could come up with (there were others but a bit uglier)
    # -----> if there is a better way to solve this problem, I'd be very happy to try it out.
    # ++++++++++++++++++
    filtered = [
        vm_snapshot
        for vm_snapshot in all_vm_snapshots
        if (
            module.params["vm_name"]
            and vm_snapshot["domain"]["name"] == query["domain.name"]
        )
        or (
            module.params["serial"]
            and vm_snapshot["domain"]["snapshotSerialNumber"]
            == query["domain.snapshotSerialNumber"]
        )
        or (module.params["label"] and vm_snapshot["label"] == query["label"])
    ]

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
