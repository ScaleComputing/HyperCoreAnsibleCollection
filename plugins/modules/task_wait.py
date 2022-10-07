#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: task_wait

author:
  - Tjaž Eržen (@tjazsch)
short_description: Wait for a HyperCore TaskTag to be finished.
description:
  - A helper module, which waits until the object with a given task_tag is actually created/updated/deleted .
  - Used within a context of a larger role. Whenever C(POST), C(PATCH) or C(DELETE) method is applied on the HyperCore
    object, a dict in with keys C(createdUUID) and C(taskTag) is returned. Depending on taskTag's status, the object's
    request might be still in queue or may be already executed. This module ensures that the object's request is not
    on queue anymore, and execution is finished.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  task_tag:
    type: dict
    description:
      - Result when calling C(POST), C(PATCH) or C(DELETE) method on the HyperCore object.
    required: true
"""


EXAMPLES = r"""
- name: Wait for the object to be created
  scale_computing.hypercore.task_wait:
    task_tag:
      createdUUID: c2d38319-db6b-4cdf-93c6-d628b47c7809
      taskTag: 1483
"""


RETURN = r"""
records:
  description:
    - The module will always return false, null, null,
  returned: success
  type: list
  sample:
    - null
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.task_tag import TaskTag
from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient


def run(module, rest_client):
    TaskTag.wait_task(rest_client, module.params["task_tag"])
    return False, None, None


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            task_tag=dict(
                type="dict",
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
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
