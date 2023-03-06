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
"""

EXAMPLES = r"""
- name: Get a list of updates
  scale_computing.hypercore.version_update_info:
  register: result
"""

RETURN = r"""
records:
  description:
    - A list of updates that can be applied to this cluster.
  returned: success
  type: list
  sample:
    - uuid: 9.2.11.210763
      description: 9.2.11 General Availability
      change_log: ...Please allow between 20-40 minutes per node for the update to complete...
      build_id: 210763
      major_version: 9
      minor_version: 2
      revision: 11
      timestamp: 0
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.rest_client import RestClient
from ..module_utils.client import Client
from ..module_utils.hypercore_version import Update
from ..module_utils.typed_classes import TypedUpdateToAnsible
from typing import List, Union


def run(rest_client: RestClient) -> List[Union[TypedUpdateToAnsible, None]]:
    return [
        Update.from_hypercore(hypercore_data=hypercore_dict).to_ansible()  # type: ignore
        for hypercore_dict in rest_client.list_records("/rest/v1/Update")
    ]


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        records = run(rest_client)
        module.exit_json(changed=False, records=records)

    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
