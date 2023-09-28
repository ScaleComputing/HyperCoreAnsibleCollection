#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: snapshot_schedule

author:
  - Tjaž Eržen (@tjazsch)
short_description: Manage snap schedule to configure the desired schedule of snapshot creation.
description:
  - Create and delete an automated VM snapshot schedule on HyperCore API endpoint C(/rest/v1/VirDomainSnapshotSchedule).
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.snapshot_schedule_info
  - module: scale_computing.hypercore.vm_replication
options:
  name:
    description:
      - Snapshot schedule's name.
      - Serves as unique identifier across all snapshot schedules.
    type: str
    required: true
  state:
    description:
      - The desired state of the snapshot schedule object.
      - Use C(absent) to ensure the snapshot schedule will be absent from the API and C(present) to ensure
        snapshot schedule will remain present on the API.
    type: str
    choices: [ present, absent ]
    required: true
  recurrences:
    description:
      - The recurrence rules we want to set for the snapshot schedule.
    type: list
    elements: dict
    default: []
    suboptions:
      name:
        type: str
        description:
          - The recurrence's name.
        required: true
      frequency:
        type: str
        description:
          - The frequency of the recurrence.
          - The value must comply with L(RFC-2445,https://www.rfc-editor.org/rfc/rfc2445).
          - A valid example is C(FREQ=WEEKLY;INTERVAL=1;BYDAY=TU).
        required: true
      start:
        type: str
        description:
          - The start of the snapshot schedule in the local timezone timestamp.
        required: true
      local_retention:
        type: int
        description:
          - Retention time in seconds.
        required: true
      remote_retention:
        type: int
        description:
          - Remote retention time in seconds.
          - If either not set or set to either C(0) or C(None), remote_retention will be assigned
            I(local_retention)'s value.
notes:
  - The C(record) return value will be changed from list (containing a single item) to dict.
    There will be no release where both old and new variant work at the same time.
    The change will happen with release 3.0.0.
    To ease migration, the only change between last 1.x or 2.x release and 3.0.0 release
    will be changing the C(record) return value.
    R(List of deprecation changes, scale_computing.hypercore.deprecation)
    includes examples to help with transition.
  - C(check_mode) is not supported.
"""


EXAMPLES = r"""
- name: Setup snapshot schedule
  scale_computing.hypercore.snapshot_schedule:
    name: demo-snap-schedule
    state: present
    recurrences:
      - name: weekly-tuesday
        frequency: "FREQ=WEEKLY;INTERVAL=1;BYDAY=TU"  # RFC-2445
        start: "2010-01-01 00:00:00"
        local_retention: "{{ 10 * 7*24*60*60 }}"  # 10 days, unit seconds
        remote_retention:  # optional, None or 0 means same as local_retention.
"""

# TODO record is list with single item, should be a dict.
RETURN = r"""
record:
  description:
    - The created or deleted snapshot schedule from the HyperCore API endpoint C(/rest/v1/VirDomainSnapshotSchedule).
  returned: success
  type: list
  elements: dict
  contains:
    uuid:
      description: Unique identifier
      type: str
      sample: 74df5b47-c468-4626-a7e4-34eca13b2f81
    name:
      description: Human-readable snapshot schedule name
      type: str
      sample: demo-snap-schedule
    recurrences:
      description: Snapshot scheduling rules
      type: list
      elements: dict
      sample:
        name: weekly-tuesday
        frequency: "FREQ=WEEKLY;INTERVAL=1;BYDAY=TU"
        start: "2010-01-01 00:00:00"
        local_retention: 1296000
        remote_retention: 3024000
        replication: true
"""

from ansible.module_utils.basic import AnsibleModule
import time

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.snapshot_schedule import SnapshotSchedule
from ..module_utils.task_tag import TaskTag


def ensure_present(module, rest_client):
    snapshot_schedule_before = SnapshotSchedule.get_by_name(module.params, rest_client)
    changed = False
    # Create record returns dict where taskTag's value is empty string. Not waiting for the task to end using TaskTag
    if snapshot_schedule_before:
        before = snapshot_schedule_before.to_ansible()
        snapshot_schedule_desired = SnapshotSchedule.from_ansible(module.params)
        if (
            snapshot_schedule_desired.recurrences
            != snapshot_schedule_before.recurrences
        ):
            # If desired and recurrence rules before differ, snapshot schedule has to be updated
            rest_client.update_record(
                "{0}/{1}".format(
                    "/rest/v1/VirDomainSnapshotSchedule", snapshot_schedule_before.uuid
                ),
                snapshot_schedule_before.create_patch_payload(
                    module.params["recurrences"]
                ),
                module.check_mode,
            )
            changed = True
    else:
        before = None
        new_snapshot_schedule = SnapshotSchedule.from_ansible(module.params)
        task = rest_client.create_record(
            "/rest/v1/VirDomainSnapshotSchedule",
            new_snapshot_schedule.create_post_payload(),
            module.check_mode,
        )
        TaskTag.wait_task(rest_client, task)
        changed = True
    after = SnapshotSchedule.get_by_name(module.params, rest_client).to_ansible()
    return changed, [after], dict(before=before, after=after)


def ensure_absent(module, rest_client):
    snapshot_schedule = SnapshotSchedule.get_by_name(module.params, rest_client)
    if snapshot_schedule:
        # No task tag is returned with DELETE on "/rest/v1/VirDomainSnapshotSchedule/{uuid}"
        task = rest_client.delete_record(
            "{0}/{1}".format(
                "/rest/v1/VirDomainSnapshotSchedule", snapshot_schedule.uuid
            ),
            module.check_mode,
        )
        if task["taskTag"] == "":
            time.sleep(1)
        output = snapshot_schedule.to_ansible()
        return True, [output], dict(before=output, after=None)
    return False, [], dict()


def run(module, rest_client):
    if module.params["state"] == "absent":
        return ensure_absent(module, rest_client)
    return ensure_present(module, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(
                type="str",
                required=True,
            ),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            recurrences=dict(
                type="list",
                elements="dict",
                default=[],
                options=dict(
                    name=dict(
                        type="str",
                        required=True,
                    ),
                    frequency=dict(
                        type="str",
                        required=True,
                    ),
                    start=dict(
                        type="str",
                        required=True,
                    ),
                    local_retention=dict(
                        type="int",
                        required=True,
                    ),
                    remote_retention=dict(
                        type="int",
                    ),
                ),
            ),
        ),
        required_if=[("state", "present", ("recurrences",))],
    )

    module.deprecate(
        "The 'record' return value will be changed from list (containing a single item) to dict. "
        "There will be no release where both old and new variant work at the same time. "
        "To ease migration, the only change between last 1.x or 2.x release and 3.0.0 release "
        "will be changing the 'record' return value. "
        "Affected modules are vm and snapshot_schedule.",
        version="3.0.0",
        collection_name="scale_computing.hypercore",
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
