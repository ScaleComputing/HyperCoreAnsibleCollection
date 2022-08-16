# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from time import sleep

from ..module_utils import errors


class TaskTag:
    @classmethod
    def wait_task(cls, rest_client, task):
        if type(task) != dict:
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
            if task_status.get("state", "") not in (
                "RUNNING",
                "QUEUED",
            ):  # TaskTag has finished
                break
            sleep(1)
