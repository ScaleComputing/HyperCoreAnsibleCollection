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
results:
  description:
    - Output from modifying Time Server configuration on HyperCore API.
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

from ..module_utils.task_tag import TaskTag
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.time_server import TimeServer


# Remove not needed
def modify_time_server(
    module: AnsibleModule, rest_client: RestClient
) -> tuple[bool, dict, dict]:
    # GET method to get the Time Server by UUID
    time_server = TimeServer.get_by_uuid(module.params, rest_client)

    # If Time Server doesn't exist, raise an exception (error)
    if not time_server:
        raise errors.ScaleComputingError(
            "Time Server: There is no Time Server configuration."
        )

    # Otherwise, continue with modifying the configuration
    before = time_server.to_ansible()
    old_state = TimeServer.get_state(
        rest_client=rest_client
    )  # get the state of Time Server before modification

    # Get new time server source host
    new_time_server_source = module.params["source"]

    # Init return values and return if no changes were made
    change, new_state, diff = (
        new_time_server_source != before.get("host"),
        old_state,
        dict(before=before, after=old_state),
    )
    if not change:
        return change, new_state, diff

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
    new_state, diff = TimeServer.get_state(rest_client), dict(
        before=before, after=after
    )
    change = old_state != new_state

    return change, new_state, diff


def run(module: AnsibleModule, rest_client: RestClient) -> tuple[bool, dict, dict]:
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
        client = Client(
            host=module.params["cluster_instance"]["host"],
            username=module.params["cluster_instance"]["username"],
            password=module.params["cluster_instance"]["password"],
        )
        rest_client = RestClient(client)
        changed, new_state, diff = run(module, rest_client)
        module.exit_json(changed=changed, new_state=new_state, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
