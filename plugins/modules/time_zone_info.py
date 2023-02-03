# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: time_zone_info

author:
  - Ana Zobec (@anazobec)
short_description: List Time Zone configuration on HyperCore API
description:
  - Use this module to list information about the DNS configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.time_server
  - module: scale_computing.hypercore.time_zone
  - module: scale_computing.hypercore.time_zone_info
"""


EXAMPLES = r"""
- name: List all Time Zone configurations on HyperCore API
  scale_computing.hypercore.time_zone_info:
  register: time_zone
"""

RETURN = r"""
record:
  description:
    - Time Zone configuration record.
  returned: success
  type: dict
  sample:
    uuid: timezone_guid
    zone: US/Eastern
    latest_task_tag:
      completed: 1675170961
      created: 1675170954
      descriptionParameters: []
      formattedDescription: TimeZone Update
      formattedMessage: ""
      messageParameters: []
      modified: 1675170961
      nodeUUIDs:
        - 32c5012d-7d7b-49b4-9201-70e02b0d8758
      objectUUID: timezone_guid
      progressPercent: 100
      sessionID: 7157e957-bfad-4506-8713-124d5eb2397d
      state: COMPLETE
      taskTag: 687
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.time_zone import TimeZone


def run(rest_client: RestClient):
    return TimeZone.get_state(rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
        ),
    )

    try:
        client = Client(
            host=module.params["cluster_instance"]["host"],
            username=module.params["cluster_instance"]["username"],
            password=module.params["cluster_instance"]["password"],
        )
        rest_client = RestClient(client)
        record = run(rest_client)
        module.exit_json(changed=False, record=record)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
