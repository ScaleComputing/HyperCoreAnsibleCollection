#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: api

author:
  - Tjaž Eržen (@tjazsch)
short_description: API interaction with Scale Computing HC3
description:
  - Perform GET, POST, PATCH, DELETE or PUT requests on resource(s) from the given endpoint
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hc3.cluster_instance
  - scale_computing.hc3.endpoint
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
      - put
  data:
    type: dict
    description:
      - A Dict consists of resource's column names as keys (such as description, number, priority, and so on) and the
        patching values as values (the value we want to change the column to).
      - If I(action==patch), data we're updating the record with.
      - If I(action==get), data with which we're going to additionally filter out the records.
      - If I(action==post), data with which we're creating the resource. Note that for certain endpoints,
        certain fields may be necessary and have to be specified here. For other columns if not specified here, they
        may be assigned the default value automatically.
      - If I(action==delete), data option is going to be ignored.
    default: {}
"""


EXAMPLES = r"""
- name: Create a VM with specified data
  scale_computing.hc3.api:
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
  scale_computing.hc3.api:
    action: get
    cluster_instance:
      host: https://0.0.0.0
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain
  register: result

- name: Retrieve a specific VM
  scale_computing.hc3.api:
    action: get
    cluster_instance:
      host: https://0.0.0.0
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain/0cdcdc95-ef66-461c-82a3-79ce03704981
  register: result

- name: Delete a VM
  scale_computing.hc3.api:
    action: delete
    cluster_instance:
      host: https://0.0.0.0
      username: admin
      password: admin
    endpoint: /rest/v1/VirDomain/0fc7fe1f-2039-42c4-a2ad-945bccbe18b2
  register: result

- name: Clone a VM from snapshot
  scale_computing.hc3.api:
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
  scale_computing.hc3.api:
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
    - Result that HC3 REST API returns when an endpoint is called.
    - The content structure is dependent on the API endpoint.
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


def patch_record(module, rest_client):
    old = rest_client.get_record(
        query=None,
        endpoint=module.params["endpoint"],
        must_exist=True,
    )
    new = rest_client.update_record(
        endpoint=module.params["endpoint"],
        payload=module.params["data"],
        check_mode=module.check_mode,
    )
    return True, new, dict(before=old, after=new)


def post_record(module, rest_client):
    record = rest_client.create_record(
        endpoint=module.params["endpoint"],
        payload=module.params["data"],
        check_mode=module.check_mode,
    )
    return (
        True,
        record,
        dict(before=None, after=record),
    )


def delete_record(module, rest_client):
    if module.params["data"]:
        module.warn("Payload will get ignored when deleting an action.")
    record = rest_client.get_record(
        endpoint=module.params["endpoint"],
        query=module.params["data"],
        must_exist=True,
    )
    rest_client.delete_record(
        endpoint=module.params["endpoint"],
        check_mode=module.check_mode,
    )
    return True, None, dict(before=record, after=None)


def put_record(module, rest_client):
    # TODO (tjazsch): Implement PUT method
    module.warn("Put methods has not been implemented yet.")
    return -1, -1, -1


def get_records(module, rest_client):
    records = rest_client.list_records(
        query=module.params["data"],
        endpoint=module.params["endpoint"],
    )
    return False, records, None


def run(module, rest_client):
    action = module.params["action"]
    if action == "patch":  # PATCH method
        return patch_record(module, rest_client)
    elif action == "post":  # POST method
        return post_record(module, rest_client)
    elif action == "get":  # GET method
        return get_records(module, rest_client)
    elif action == "put":  # GET method
        return put_record(module, rest_client)
    return delete_record(module, rest_client)  # DELETE methodx


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance", "endpoint", "action"),
            data=dict(
                type="dict",
                default=dict(),
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
