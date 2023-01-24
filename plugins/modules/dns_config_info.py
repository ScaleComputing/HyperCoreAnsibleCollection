# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: dns_config_info

author:
  - Ana Zobec (@anazobec)
short_description: List DNS configuration on HyperCore API
description:
  - Use this module to list information about the DNS configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.dns_config
"""


EXAMPLES = r"""
- name: List all configurations on DNS configuration on HyperCore API
  scale_computing.hypercore.dns_config_info:
  register: dns_config
"""

RETURN = r"""
records:
  description:
    - A list of DNS configuration records.
  returned: success
  type: dict
  sample:
    uuid: "dnsconfig_guid"
    server_ips:
      - "1.1.1.1"
      - "1.0.0.1"
    search_domains: []
    latest_task_tag:
      completed: 1673946776
      created: 1673946770
      descriptionParameters: []
      formattedDescription: "DNSConfig Update"
      formattedMessage: ""
      messageParameters: []
      modified: 1673946776
      nodeUUIDs:
        - "32c5012d-7d7b-49b4-9201-70e02b0d8758"
      objectUUID: "dnsconfig_guid"
      progressPercent: 100
      sessionID: "775155cc-bc4e-445c-9efa-a304f4f66c82"
      state: "COMPLETE"
      taskTag: "359"
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.dns_config import DNSConfig


def run(rest_client: RestClient):
    return DNSConfig.get_state(rest_client)


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
        records = run(rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
