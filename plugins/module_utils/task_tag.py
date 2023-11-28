# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from time import sleep

from ..module_utils import errors
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import TypedTaskTag
from typing import Optional, Dict, Any


class TaskTag:
    @classmethod
    def wait_task(
        cls,
        rest_client: RestClient,
        task: Optional[TypedTaskTag],
        check_mode: bool = False,
    ) -> None:
        if check_mode:
            return
        if task is None:
            return
        if not isinstance(task, dict):
            raise errors.ScaleComputingError("task should be dictionary.")
        if "taskTag" not in task.keys():
            raise errors.ScaleComputingError("taskTag is not in task dictionary.")
        if not task["taskTag"]:
            return

        while True:
            task_status = rest_client.get_record(
                "{0}/{1}".format("/rest/v1/TaskTag", task["taskTag"]), query={}
            )
            if task_status is None:  # No such task_status is found
                break
            if task_status.get("state", "") in (
                "ERROR",
                "UNINITIALIZED",
            ):  # TaskTag has finished unsucessfully or was never initialized, both are errors.
                raise errors.TaskTagError(task_status)
            if task_status.get("state", "") not in (
                "RUNNING",
                "QUEUED",
            ):  # TaskTag has finished
                break
            sleep(1)

    @staticmethod
    def get_task_status(
        rest_client: RestClient, task: Optional[TypedTaskTag]
    ) -> Optional[Dict[Any, Any]]:
        if not task:
            return None
        if not isinstance(task, dict):
            raise errors.ScaleComputingError("task should be dictionary.")
        if "taskTag" not in task.keys():
            raise errors.ScaleComputingError("taskTag is not in task dictionary.")
        if not task["taskTag"]:
            return None
        task_status: Optional[Dict[Any, Any]] = rest_client.get_record(
            "{0}/{1}".format("/rest/v1/TaskTag", task["taskTag"]), query={}
        )
        return task_status if task_status else None
