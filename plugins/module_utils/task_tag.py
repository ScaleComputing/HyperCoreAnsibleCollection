# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from time import sleep

from ..module_utils.errors import MissingFunctionParameter


class TaskTag:
    @classmethod
    def get_task_by_task_tag(cls, client, task_tag):
        if task_tag:
            end_point = "/rest/v1/TaskTag"
            task = client.request("GET", end_point + "/" + task_tag).json[0]
            return task
        else:
            raise MissingFunctionParameter(
                "task_tag - task_tag.py - get_task_by_task_tag()"
            )

    @classmethod
    def wait_task(cls, client, task):
        if type(task) != dict:
            raise errors.ScaleComputingError("task should be dictionary.")
        if "taskTag" not in task.keys():
            raise errors.ScaleComputingError("taskTag is not in task dictionary.")

        task_status = TaskTag.get_task_by_task_tag(client, task["taskTag"])
        while (
            type(task_status) == dict
            and "state" in task_status.keys()
            and task_status["state"] in ["RUNNING", "QUEUED"]
        ):
            sleep(1)
            task_status = TaskTag.get_task_by_task_tag(client, task["taskTag"])
