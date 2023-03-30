#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: version_update_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Get a list of updates that can be applied to this cluster.
description:
  - Get a list of updates that can be applied to this cluster.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.version_update
  - module: scale_computing.hypercore.version_update_status_info
options:
  select:
    description:
      - List desired version update from list of updates
      - If C(next), then version with the lowest number in the list of available updates is returned
      - If C(latest), then version with the highest number in the list of available updates is returned
    type: str
    choices: [ next, latest ]
"""

EXAMPLES = r"""
- name: Get a list of updates
  scale_computing.hypercore.version_update_info:
  register: result

- name: Get a list of updates and next update
  scale_computing.hypercore.version_update_info:
    select: next
  register: result

- name: Get a list of updates and latest update
  scale_computing.hypercore.version_update_info:
    select: latest
  register: result
"""

RETURN = r"""
records:
  description:
    - A list of updates that can be applied to this cluster.
  returned: success
  type: list
  contains:
    uuid:
      description: Unique identifier in format majorVersion.minorVersion.revision.buildID
      type: str
      sample: 9.2.11.210763
    description:
      description: Human-readable name for the update
      type: str
      sample: 9.2.11 General Availability
    change_log:
      description: Description of all changes that are in this update, in HTML format
      type: str
      sample: ...Please allow between 20-40 minutes per node for the update to complete...
    build_id:
      description: ID of the build which corresponds to this update
      type: int
      sample: 210763
    major_version:
      description: Major version number
      type: int
      sample: 9
    minor_version:
      description: Minor version number
      type: int
      sample: 2
    revision:
      description: Revision number
      type: int
      sample: 11
    timestamp:
      description: Unix timestamp when the update was released
      type: int
      sample: 0
record:
  description:
    - Next or latest update from list of updates, when option I(select) is specified
  returned: success
  type: dict
  contains:
    uuid:
      description: Unique identifier in format majorVersion.minorVersion.revision.buildID
      type: str
      sample: 9.2.11.210763
    description:
      description: Human-readable name for the update
      type: str
      sample: 9.2.11 General Availability
    change_log:
      description: Description of all changes that are in this update, in HTML format
      type: str
      sample: ...Please allow between 20-40 minutes per node for the update to complete...
    build_id:
      description: ID of the build which corresponds to this update
      type: int
      sample: 210763
    major_version:
      description: Major version number
      type: int
      sample: 9
    minor_version:
      description: Minor version number
      type: int
      sample: 2
    revision:
      description: Revision number
      type: int
      sample: 11
    timestamp:
      description: Unix timestamp when the update was released
      type: int
      sample: 0
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.rest_client import RestClient
from ..module_utils.client import Client
from ..module_utils.hypercore_version import Update
from ..module_utils.typed_classes import TypedUpdateToAnsible
from typing import List, Optional, Tuple
import operator


def select_next_or_latest(
    list_of_updates: List[TypedUpdateToAnsible], next_or_latest: str
) -> Optional[TypedUpdateToAnsible]:
    if not list_of_updates:
        return None
    sorted_list = list_of_updates.copy()  # so that we keep original records
    sorted_list.sort(
        key=operator.itemgetter(
            "major_version", "minor_version", "revision", "build_id"
        )
    )
    if next_or_latest == "next":
        return sorted_list[0]
    else:
        return sorted_list[-1]


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[List[Optional[TypedUpdateToAnsible]], Optional[TypedUpdateToAnsible]]:
    record = None
    records = [
        Update.from_hypercore(hypercore_data=hypercore_dict).to_ansible()  # type: ignore
        for hypercore_dict in rest_client.list_records("/rest/v1/Update")
    ]
    if module.params["select"]:
        record = select_next_or_latest(records, module.params["select"])
    return records, record


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            select=dict(type="str", choices=["next", "latest"]),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        records, record = run(module, rest_client)
        module.exit_json(changed=False, records=records, record=record)

    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
