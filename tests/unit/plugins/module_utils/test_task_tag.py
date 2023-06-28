# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag import (
    TaskTag,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)

error_task_tag = {
    "taskTag": "36199",
    "progressPercent": 0,
    "state": "ERROR",
    "formattedDescription": "Delete block device %@ for Virtual Machine %@",
    "descriptionParameters": ["3aad4f9d", "demo-vm"],
    "formattedMessage": "Unable to delete block device from VM '%@': Still in use",
    "messageParameters": ["demo-vm"],
    "objectUUID": "8c6196be-ddb5-4357-9783-50869dc60969",
    "created": 1687925214,
    "modified": 1687925276,
    "completed": 1687925276,
    "sessionID": "d4fa7269-caa0-4a0a-b5d8-85d8601e93c4",
    "nodeUUIDs": ["3dcb0c96-f013-4ccc-b639-33605ea78c44"],
}


ok_task_tag = {
    "taskTag": "10",
    "progressPercent": 100,
    "state": "COMPLETE",
    "formattedDescription": "Delete Alert Email Target",
    "descriptionParameters": [],
    "formattedMessage": "",
    "messageParameters": [],
    "objectUUID": "default-target",
    "created": 1686128448,
    "modified": 1686128448,
    "completed": 1686128448,
    "sessionID": "d339e80b-e2a9-4b81-a55f-d1d13d6c8645",
    "nodeUUIDs": [],
}


class TestTaskTag:
    def test_wait_task_ok(self, mocker):
        task = dict(taskTag=10)
        rest_client = mocker.MagicMock()
        rest_client.get_record.return_value = ok_task_tag
        TaskTag.wait_task(rest_client, task)

    def test_wait_task_error(self, mocker):
        # Ensure a meaningful error message is shown in ansible stderr if tasktag fails.
        task = dict(taskTag=36199)
        rest_client = mocker.MagicMock()
        rest_client.get_record.return_value = error_task_tag
        with pytest.raises(
            errors.ScaleComputingError,
            match="There was a problem during this task execution. Task details: "
            + '{"taskTag": "36199", "progressPercent": 0, "state": "ERROR",',
        ):
            TaskTag.wait_task(rest_client, task)
