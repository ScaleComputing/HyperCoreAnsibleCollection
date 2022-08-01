#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Create or update VM
description:
  - Module creates a new VM or updates existing VM.
version_added: 0.0.1
extends_documentation_fragment: []
seealso: []
options:
  host: #
    description:
      - Host address.
    type: str
    required: true
  username: #
    description:
      - Scale Computing HC3 username
    type: str
    required: true
  password: #
    description:
      - Scale Computing HC3 API password
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Create a VM
  scale_computing.hc3.vm:
    name: demo-vm
    # TODO
  register: result
"""

RETURN = r"""
vm:
  description:
    - A single VM record.
  returned: success
  type: dict  #?
  sample:
    name: "vm-name"
    uuid: "1234-0001"
    state: "running"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors
from ..module_utils.client import Client


def create_post_body(module):
    post_body = {}

    optional = {"attachGuestToolsISO": module.params["attachGuestToolsISO"]}
    # ne vem, kaj module.params.pop naredi. To ni navaden dict.pop?
    module.params.pop("username", None)
    module.params.pop("password", None)
    module.params.pop("host", None)
    module.params.pop("attachGuestToolsISO", None)
    module.params["blockDevs"] = module.params["disks"]
    module.params.pop("disks", None)
    module.params["mem"] = module.params["memory"]
    module.params.pop("memory", None)
    module.params["netDevs"] = module.params["nics"]
    module.params.pop("nics", None)

    post_body["dom"] = module.params
    post_body["options"] = optional

    return post_body


def run(module, client):
    end_point = "/rest/v1/VirDomain"

    # TODO check if VM already exists, modify it if it needs to be modified.
    data = create_post_body(module)
    json_response = client.request("POST", end_point, data=data).json

    return json_response


def main():
    module = AnsibleModule(
        supports_check_mode=True,  # False ATM
        argument_spec=dict(
            host=dict(
                type="str",
                required=True,
            ),
            password=dict(
                type="str",
                required=True,
            ),
            username=dict(
                type="str",
                required=True,
            ),
            name=dict(
                type="str",
            ),
            description=dict(
                type="str",
            ),
            memory=dict(
                type="int",
            ),
            numVCPU=dict(
                type="int",
            ),
            state=dict(
                type="str",
                choices=[
                    "RUNNING",
                    "BLOCKED",
                    "PAUSED",
                    "SHUTDOWN",
                    "SHUTOFF",
                    "CRASHED",
                ],
            ),
            tags=dict(
                type="str",
            ),
            disks=dict(
                type="list",
                elements="dict",
            ),
            nics=dict(
                type="list",
                elements="dict",
            ),
            boot_devices=dict(
                type="list",
                elements="dict",
            ),
            cloud_init=dict(
                type="dict",
            ),
            attachGuestToolsISO=dict(
                type="bool",
            ),
        ),
        mutually_exclusive=[
            ("name", "uuid"),
        ],
    )

    try:
        host = module.params["host"]
        username = module.params["username"]
        password = module.params["password"]
        client = Client(host, username, password)
        vms = run(module, client)
        module.exit_json(changed=False, vms=vms)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
