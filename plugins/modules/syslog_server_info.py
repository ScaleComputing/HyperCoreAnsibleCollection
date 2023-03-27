#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: syslog_server_info

author:
  - Ana Zobec (@anazobec)
short_description: List Syslog servers on HyperCore API
description:
  - Use this module to list information about the Syslog servers configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.syslog_server
"""


EXAMPLES = r"""
- name: List all Syslog servers on HyperCore API
  scale_computing.hypercore.syslog_server_info:
  register: syslog_server
"""

RETURN = r"""
records:
  description:
    - A list of Syslog servers records.
  returned: success
  type: list
  elements: dict
  contains:
    alert_tag_uuid:
      description: Unique identifier for an AlertTag (internal)
      type: str
      sample: 0
    host:
      description: IP address or hostname of the syslog server
      type: str
      sample: 10.5.11.222
    latest_task_tag:
      description: Latest Task Tag
      type: dict
      sample:
        completed: 1623069193
        created: 1623069187
        descriptionParameters: []
        formattedDescription: Create Alert Syslog Target
        formattedMessage: ""
        messageParameters: []
        modified: 1623069193
        nodeUUIDs:
          - 32c5012d-7d7b-49b4-9201-70e02b0d8758
        objectUUID: 21c65667-234a-437b-aead-df0199598ff9
        progressPercent: 100
        sessionID: ""
        state: COMPLETE
        taskTag: 13
    port:
      description: Network port of the syslog server
      type: int
      sample: 514
    protocol:
      description: Network protocol used to send syslog alerts
      type: str
      sample: udp
    resend_delay:
      description: Alert resend delay in seconds
      type: int
      sample: 86400
    silent_period:
      description: Alerts will not resend if there are additional event triggers within this time in seconds
      type: str
      sample: 900
    uuid:
      description: Unique identifer
      type: str
      sample: 21c65667-234a-437b-aead-df0199598ff9
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.syslog_server import SyslogServer
from ..module_utils.typed_classes import TypedSyslogServerToAnsible
from typing import List, Optional


def run(rest_client: RestClient) -> List[Optional[TypedSyslogServerToAnsible]]:
    return SyslogServer.get_state(rest_client)


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
