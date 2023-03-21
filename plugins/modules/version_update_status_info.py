#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: version_update_status_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Returns status of the latest update applied.
description:
  - Returns status of the latest update applied.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.version_update
  - module: scale_computing.hypercore.version_update_info
"""

EXAMPLES = r"""
- name: Get status of the latest update applied
  scale_computing.hypercore.version_update_status_info:
  register: result
"""

RETURN = r"""
record:
  description:
    - Status of the latest update applied
    - None/null is returned if no update was ever applied.
  returned: success
  type: dict
  sample:
    - from_build: 207183
      percent: 100
      prepare_status: ""
      update_status: COMPLETE
      update_status_details: Update Complete. Press 'Reload' to reconnect
      usernotes: ""
      to_build: 209840
      to_version: 9.1.18.209840
"""

from typing import Optional
from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.rest_client import RestClient
from ..module_utils.client import Client
from ..module_utils.hypercore_version import UpdateStatus
from ..module_utils.typed_classes import TypedUpdateStatusToAnsible


def run(rest_client: RestClient) -> Optional[TypedUpdateStatusToAnsible]:
    status = UpdateStatus.get(rest_client)
    if status:
        return status.to_ansible()
    return None


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
        record = run(rest_client)
        module.exit_json(record=record)

    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
