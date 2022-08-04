# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from time import sleep


class TaskTag:
    @classmethod
    def get_task_by_task_tag(cls, client, task_tag):
        # we do not to return just the first of all tags, if function is called with task_tag="" due to typo.s
        assert task_tag
        end_point = "/rest/v1/TaskTag"
        task = client.request("GET", end_point + "/" + task_tag).json[0]
        return task


    @classmethod
    def wait_task(cls, client, task):
        if type(task) == dict and "taskTag" in task.keys():
            task_status = TaskTag.get_task_by_task_tag(client, task["taskTag"])
            while (
                type(task_status) == dict
                and "state" in task_status.keys()
                and task_status["state"] in ["RUNNING", "QUEUED"]
            ):
                sleep(1)
                task_status = TaskTag.get_task_by_task_tag(client, task["taskTag"])
