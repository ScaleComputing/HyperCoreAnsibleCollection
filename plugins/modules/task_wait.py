#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: task_wait

author:
  - Tjaž Eržen (@tjazsch)
short_description: Wait for the object with given task_tag to be created.
description:
  - Helper module, which waits till the object with the given task_tag is actually created
  - Usually used within a context of a larger role. Whenever POST, PATCH or DELETE method is applied on the HC3
    object, a dict in with keys createdUUID and taskTag is returned. Depending on taskTag's status, the object's
    request might be still in queue or may be already executed. This module ensures that the object's request is not
    on queue anymore.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hc3.cluster_instance
seealso: []
options:
  task_tag:
    type: dict
    description:
      - Result when calling POST, PATCH or DELETE method on the HC3 object.
    required: true
"""


EXAMPLES = r"""
- name: Wait for the object to be created
  scale_computing.hc3.task_wait:
    task_tag:
      createdUUID: c2d38319-db6b-4cdf-93c6-d628b47c7809
      taskTag: 1483
"""


RETURN = r"""
records:
  description:
    - True module will always return false, null, null,
  returned: success
  type: list
  sample:
    - null
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.task_tag import TaskTag
from ..module_utils import errors, arguments
from ..module_utils.client import Client


def run(module, client):
    TaskTag.wait_task(client, module.params["task_tag"])
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
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
