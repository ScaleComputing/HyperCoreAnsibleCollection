#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: api

author:
  - Tjaž Eržen (@tjazsch)
short_description: API interaction with Scale Computing HyperCore
description:
  - Perform a C(GET), C(POST), C(PATCH), C(DELETE), or C(PUT) request on resource(s) from the given endpoint.
    The api module can be used to perform raw API calls whenever there is no
    suitable concrete module or role implementation for a specific task.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.endpoint
seealso: []
options:
  action:
    description:
      - The action to perform.
    type: str
    required: true
    choices:
      - post
      - patch
      - delete
      - get
      - post_list
      - put
  data:
    type: dict
    description:
      - A Dict containing a data to be sent to HyperCore REST endpoint.
      - If I(action=patch), data we're updating the resource with.
      - If I(action=get), data option is going to be ignored.
      - If I(action=post) the resource will be created from the data.
      - If I(action=delete), data option is going to be ignored.
      - If I(action=post_list), data will be send as list instead of dict.
  endpoint:
    description:
      - The raw endpoint that we want to perform post, patch or delete operation on.
    type: str
    required: true
notes:
  - C(check_mode) is not supported.

"""


EXAMPLES = r"""
- name: Create a VM with specified data
  scale_computing.hypercore.api:
    action: post
    cluster_instance:
      host: "https://0.0.0.0"
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain
    data:
      dom:
        name: XLAB-jc1
        tags: Xlab,jc1,us1
        mem: 512100100
        numVCPU: 2
        blockDevs:
          - type: VIRTIO_DISK
            capacity: 8100100100
            name: jc1-disk-0
        netDevs:
          - type: RTL8139
            vlan: 0
            connected: true
      options:
        attachGuestToolsISO: true
  register: result

- name: Retrieve all VMs
  scale_computing.hypercore.api:
    action: get
    cluster_instance:
      host: https://0.0.0.0
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain
  register: result

- name: Retrieve a specific VM
  scale_computing.hypercore.api:
    action: get
    cluster_instance:
      host: https://0.0.0.0
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain/0cdcdc95-ef66-461c-82a3-79ce03704981
  register: result

- name: Delete a VM
  scale_computing.hypercore.api:
    action: delete
    cluster_instance:
      host: https://0.0.0.0
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain/0fc7fe1f-2039-42c4-a2ad-945bccbe18b2
  register: result

- name: Clone a VM from snapshot
  scale_computing.hypercore.api:
    action: post
    cluster_instance:
      host: https://0.0.0.0
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain/17a23be5-9cf2-4d79-b02f-b2a0cb29a0f7/clone
    data:
      template:
        name: XLAB-jc1
        description: ""
        tags: Xlab,jc1,us1
  register: result

- name: Patch (an existing) record
  scale_computing.hypercore.api:
    action: post
    cluster_instance:
      host: https://0.0.0.0
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain/17a23be5-9cf2-4d79-b02f-b2a0cb29a0f7
    data:
      dom:
        name: XLAB-jc1-updated
        tags: Xlab,jc1,us1,updated-tag
        mem: 512100100
        numVCPU: 2
        blockDevs:
          - type: VIRTIO_DISK
            capacity: 8100100100
            name: jc1-disk-0-updated
        netDevs:
          - type: RTL8139
            vlan: 0
            connected: true
      options:
        attachGuestToolsISO: true
  register: result
"""


RETURN = r"""
records:
  description:
    - In case of I(action=get), the records from the specified endpoint. Below is example output for I(action=get).
    - In case of I(action=post), I(action=patch) or I(action=delete), the task tag, returned from the HyperCore API.
  returned: success
  type: list
  sample:
    - uuid: 81178af9-fb4c-4e98-9dba-d272adc2cae2
      virDomainUUID: 17a23be5-9cf2-4d79-b02f-b2a0cb29a0f7
      type: RTL8139
      macAddress: 7C:4C:58:18:23:4F
      connected: true
      ipv4Addresses: []
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.task_tag import TaskTag


def patch_record(module, rest_client):
    old = rest_client.get_record(
        query=None,
        endpoint=module.params["endpoint"],
        must_exist=True,
    )
    task_tag = rest_client.update_record(
        endpoint=module.params["endpoint"],
        payload=module.params["data"],
        check_mode=module.check_mode,
    )
    TaskTag.wait_task(rest_client, task_tag)
    new = rest_client.get_record(
        query=None,
        endpoint=module.params["endpoint"],
        must_exist=True,
    )
    changed = False if old == new else True
    return changed, task_tag


def post_record(module, rest_client):
    task_tag = rest_client.create_record(
        endpoint=module.params["endpoint"],
        payload=module.params["data"],
        check_mode=module.check_mode,
    )
    TaskTag.wait_task(rest_client, task_tag)
    return True, task_tag


def post_list_record(module, rest_client):
    task_tag = rest_client.create_record(
        endpoint=module.params["endpoint"],
        payload=[module.params["data"]],
        check_mode=module.check_mode,
    )
    TaskTag.wait_task(rest_client, task_tag)
    return True, task_tag


def delete_record(module, rest_client):
    if module.params["data"]:
        module.warn("Payload will get ignored when deleting an action.")
    record = rest_client.get_record(
        endpoint=module.params["endpoint"],
        query=module.params["data"],
        must_exist=False,
    )
    if record:
        task_tag = rest_client.delete_record(
            endpoint=module.params["endpoint"],
            check_mode=module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag)
        return True, task_tag
    return False, dict()

"""
PUT_TIMEOUT_TIME was copied from the iso module for ISO data upload.
Currently, assume we have 4.7 GB ISO and speed 1 MB/s -> 4700 seconds.
Rounded to 3600.

TODO: compute it from expected min upload speed and file size.
Even better, try to detect stalled uploads and terminate if no data was transmitted for more than N seconds.
Yum/dnf complain with error "Operation too slow. Less than 1000 bytes/sec transferred the last 30 seconds"
in such case.
"""
PUT_TIMEOUT_TIME = 3600

def put_record(module, rest_client):
    with open(module.params["source"], "rb") as source_file:
      result = rest_client.put_record(
        endpoint=module.params["endpoint"],
        payload=None,
        check_mode=module.check_mode,
        query=module.params["data"],
        timeout=PUT_TIMEOUT_TIME,
        binary_data=source_file,
        headers={
          "Content-Type": "application/octet-stream",
          "Accept": "application/json",
        }
      )
    return True, result


def get_records(module, rest_client):
    records = rest_client.list_records(
        query=module.params["data"],
        endpoint=module.params["endpoint"],
    )
    return False, records


def run(module, rest_client):
    action = module.params["action"]
    if action == "patch":  # PATCH method
        return patch_record(module, rest_client)
    elif action == "post":  # POST method
        return post_record(module, rest_client)
    elif action == "post_list":  # POST method, but sends list instead of dict
        return post_list_record(module, rest_client)
    elif action == "get":  # GET method
        return get_records(module, rest_client)
    elif action == "put":  # PUT method
        return put_record(module, rest_client)
    return delete_record(module, rest_client)  # DELETE methodx


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            data=dict(
                type="dict",
            ),
            action=dict(
                type="str",
                choices=["post", "patch", "delete", "get", "post_list", "put"],
                required=True,
            ),
            endpoint=dict(
                type="str",
                required=True,
            ),
            source=dict(
                type="str",
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record = run(module, rest_client)
        module.exit_json(changed=changed, record=record)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
