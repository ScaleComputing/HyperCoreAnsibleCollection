#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: time_server

author:
  - Ana Zobec (@anazobec)
short_description: Modify Time Zone configuration on HyperCore API
description:
  - Use this module to modify an existing Time Zone configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.time_server_info
  - module: scale_computing.hypercore.time_zone
  - module: scale_computing.hypercore.time_zone_info
options:
  source:
    type: str
    description:
      - A NTP server string used to replace the existing one.
      - If the given NTP server already exist in the Time Server configuration,
        there will be no changes made.
    required: True
notes:
 - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Change NTP server
  scale_computing.hypercore.time_server:
    source: europe.pool.ntp.org
"""

RETURN = r"""
record:
  description:
    - Output from modifying Time Server configuration on HyperCore API.
  returned: success
  type: dict
  contains:
    uuid:
      description: Unique identifer
      type: str
      sample: timesource_guid
    host:
      description: IP address or hostname of the time source server
      type: str
      sample: pool.ntp.org
    latest_task_tag:
      description: Latest Task Tag
      type: dict
      sample:
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

from typing import Tuple
from ansible.module_utils.basic import AnsibleModule

from ..module_utils.task_tag import TaskTag
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.time_server import TimeServer


# Remove not needed
def modify_time_server(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, dict, dict]:
    # GET method to get the Time Server by UUID
    time_server = TimeServer.get_by_uuid(module.params, rest_client)

    # Get new time_server source host
    new_time_server_source = module.params["source"]

    # If Time Server doesn't exist, create one
    if not time_server:
        create_task_tag = rest_client.create_record(
            endpoint="/rest/v1/TimeSource",
            payload=dict(host=new_time_server_source),
            check_mode=module.check_mode,
        )
        TaskTag.wait_task(rest_client, create_task_tag)
        after = TimeServer.get_state(rest_client)
        return True, {}, dict(before={}, after=after)

    # Otherwise, continue with modifying the configuration
    before = time_server.to_ansible()
    old_state = TimeServer.get_state(
        rest_client=rest_client
    )  # get the state of Time Server before modification

    # Init return values and return if no changes were made
    change, record, diff = (
        new_time_server_source != before.get("host"),
        old_state,
        dict(before=before, after=old_state),
    )
    if not change:
        return change, record, diff

    # Set the task tag:
    # update_record -> PATCH
    update_task_tag = rest_client.update_record(
        endpoint="{0}/{1}".format("/rest/v1/TimeSource", time_server.uuid),
        payload=dict(host=new_time_server_source),
        check_mode=module.check_mode,
    )

    TaskTag.wait_task(rest_client, update_task_tag)  # wait for the task to finish

    new_time_server = TimeServer.get_by_uuid(module.params, rest_client)
    after = new_time_server.to_ansible()
    record, diff = TimeServer.get_state(rest_client), dict(before=before, after=after)
    change = old_state != record

    return change, record, diff


def run(module: AnsibleModule, rest_client: RestClient) -> Tuple[bool, dict, dict]:
    return modify_time_server(module, rest_client)


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            source=dict(
                type="str",
                required=True,
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
