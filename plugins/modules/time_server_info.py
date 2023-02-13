# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# DOCUMENTATION = r"""
# module: time_server_info
#
# author:
#   - Ana Zobec (@anazobec)
# short_description: List Time Server source configuration on HyperCore API.
# description:
#   - Use this module to list information about the Time Server configuration on HyperCore API.
# version_added: 1.2.0
# extends_documentation_fragment:
#   - scale_computing.hypercore.cluster_instance
# seealso:
#   - module: scale_computing.hypercore.time_server
#   - module: scale_computing.hypercore.time_zone
#   - module: scale_computing.hypercore.time_zone_info
# """

DOCUMENTATION = r"""
module: time_server_info

author:
  - Ana Zobec (@anazobec)
short_description: List Time Server configuration on HyperCore API.
description:
  - Use this module to list information about the Time Server configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.time_server
  - module: scale_computing.hypercore.time_zone
  - module: scale_computing.hypercore.time_zone_info
"""


EXAMPLES = r"""
- name: List all Time Server source configurations on HyperCore API
  scale_computing.hypercore.time_server_info:
  register: time_server
"""

RETURN = r"""
record:
  description:
    - Time Server configuration record.
  returned: success
  type: dict
  sample:
    uuid: timesource_guid
    host: pool.ntp.org
    latest_task_tag:
      completed: 1675169105
      created: 1675169100
      descriptionParameters: []
      formattedDescription: TimeSource Update
      formattedMessage: ""
      messageParameters: []
      modified: 1675169105
      nodeUUIDs:
        - 32c5012d-7d7b-49b4-9201-70e02b0d8758
      objectUUID: timesource_guid
      progressPercent: 100
      sessionID: b0ef6ff6-e7dc-4b13-80f2-010e1bcbcfbf
      state: COMPLETE
      taskTag: 665
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.time_server import TimeServer


def run(rest_client: RestClient):
    return TimeServer.get_state(rest_client)


def main():
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
        module.exit_json(changed=False, record=record)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
