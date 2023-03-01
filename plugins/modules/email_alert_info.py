#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: email_alert_info

author:
  - Ana Zobec (@anazobec)
short_description: List Email Alert Recipients on HyperCore API
description:
  - Use this module to list information about the DNS configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.email_alert
"""


EXAMPLES = r"""
- name: List all Email Alert Recipients on HyperCore API
  scale_computing.hypercore.email_alert_info:
  register: email_alert
"""

RETURN = r"""
records:
  description:
    - A list of Email Alert Recipient records.
  returned: success
  type: list
  sample:
    - alert_tag_uuid: 0
      email: sample@sample.com
      latest_task_tag:
        completed: 1675680830
        created: 1675680830
        descriptionParameters: []
        formattedDescription: Create Alert Email Target
        formattedMessage: ""
        messageParameters: []
        modified: 1675680830
        nodeUUIDs: []
        objectUUID: 8664ed18-c354-4bab-be96-78dae5f6377f
        progressPercent: 100
        sessionID: 2bed8c34-1ef3-4366-8895-360f4f786afe
        state: COMPLETE
        taskTag: 813
      resend_delay: 86400
      silent_period: 900
      uuid: 8664ed18-c354-4bab-be96-78dae5f6377f
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.email_alert import EmailAlert
from ..module_utils.typed_classes import TypedEmailAlertToAnsible
from typing import List, Union


def run(rest_client: RestClient) -> List[Union[TypedEmailAlertToAnsible, None]]:
    return EmailAlert.get_state(rest_client)


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
