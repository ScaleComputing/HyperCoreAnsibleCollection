#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: snapshot_schedule_info

author:
  - Tjaž Eržen (@tjazsch)
short_description: Retrieve information about an automated VM snapshot schedule.
description:
  - Retrieve information about an automated VM snapshot schedule on HyperCore API endpoint C(/rest/v1/VirDomainSnapshotSchedule).
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.snapshot_schedule
options:
  name:
    description:
      - Snapshot schedule's name.
      - If specified, specific snapshot schedule is going to be obtained.
      - Otherwise, all snapshot schedules are going to be listed.
    type: str
"""


EXAMPLES = r"""
- name: List specific snapshot schedule
  scale_computing.hypercore.snapshot_schedule_info:
    name: demo-snap-schedule
  register: result

- name: List all snapshot schedules
  scale_computing.hypercore.snapshot_schedule_info:
  register: result
"""


RETURN = r"""
records:
  description:
    - Records from the HyperCore API endpoint C(/rest/v1/VirDomainSnapshotSchedule).
  returned: success
  type: dict
  sample:
    uuid: 74df5b47-c468-4626-a7e4-34eca13b2f81
    name: demo-snap-schedule
    recurrences:
      - name: weekly-tuesday
        frequency: "FREQ=WEEKLY;INTERVAL=1;BYDAY=TU"
        start: "2010-01-01 00:00:00"
        local_retention: 1296000
        remote_retention: 3024000
        replication: true
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.utils import get_query
from ..module_utils.snapshot_schedule import SnapshotSchedule


def run(module, rest_client):
    query = get_query(module.params, "name", ansible_hypercore_map=dict(name="name"))
    return [
        SnapshotSchedule.from_hypercore(hypercore_dict).to_ansible()
        for hypercore_dict in rest_client.list_records(
            "/rest/v1/VirDomainSnapshotSchedule", query
        )
    ]


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(
                type="str",
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]
        client = Client(host, username, password)
        rest_client = RestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
