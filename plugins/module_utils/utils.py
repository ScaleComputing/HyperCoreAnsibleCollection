# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import uuid
from time import sleep


# return values is not needed - exception is raised
# rename to validate_uuid()?
def is_valid_uuid(value):
    try:
        uuid.UUID(value, version=4)
    except ValueError:
        # better error message
        raise ValueError("invalid uuid={value}, check UUID in playbook")
    return True


def get_nic_by_uuid(client, nic_uuid):
    json_response = ""  # not needed
    if is_valid_uuid(nic_uuid):  # exception is raised
        end_point = "/rest/v1/VirDomainNetDevice/" + nic_uuid
        json_response = client.request("GET", end_point).json  # this is dict, right?
    return json_response  # dict or str, difficult to use
    # define a Nic class.
    # classmethod Nic.get(client, uuid=None)
    # classmethod Nic.find(client, mac=None, vlan=None)
    #   search by the provided param(s), more than one object might match.
    #   get_all_nics() == Nic.find(client)
    # sidenote - "/rest/v1/VirDomainNetDevice/{uuid}" - it does not tell to which VM is NIC assigned (field is None or [] or similar).
    # Nic class should contain all attributes that will be returned by vm_nic_info module?


def get_all_nics(client):
    end_point = "/rest/v1/VirDomainNetDevice"
    json_response = client.request("GET", end_point).json
    return json_response


# get_nic_by_uuid has client as first param, here is client a second.
def get_task_by_task_tag(task_tag, client):
    end_point = "/rest/v1/TaskTag"
    task = client.request("GET", end_point + "/" + task_tag).json[0]
    return task
    # what is returned if task_tag is invalid? I would expect None.


def wait_task(task, client):
    if type(task) == dict and "taskTag" in task.keys():
        task_status = get_task_by_task_tag(task["taskTag"], client)
        # task_status["state"] in ["RUNNING", "QUEUED"]
        while(type(task_status) == dict and "state" in task_status.keys() and task_status["state"] == "RUNNING" or task_status["state"] == "QUEUED"):
            sleep(1)
            task_status = get_task_by_task_tag(task["taskTag"], client)
