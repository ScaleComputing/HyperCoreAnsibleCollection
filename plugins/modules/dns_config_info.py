#!/usr/bin/python
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
record:
  description:
    - DNS configuration record.
  returned: success
  type: dict
  contains:
    uuid:
      description: Unique identifer
      type: str
      sample: dnsconfig_guid
    server_ips:
      description: IP address or hostname of DNS servers
      type: list
      elements: str
      sample: 1.1.1.1
    search_domains:
      description: Domain search list used to resolve fully qualified domain names
      type: list
      elements: str
      sample: example.domain1.com
    latest_task_tag:
      description: Latest Task Tag
      type: dict
      sample:
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
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        record = run(rest_client)
        module.exit_json(changed=False, record=record)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
