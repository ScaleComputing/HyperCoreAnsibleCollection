#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function
from typing_extensions import Required

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_nic_info

author:
  - First Second (@firstsecond)
short_description: Sample plugin
description:
  - A sample plugin with boilerplate code.
version_added: 0.0.1
extends_documentation_fragment: []
seealso: []
options:
  host:
    description:
      - Host address.
    type: str
    required: true
  username:
    description:
      - Scale computing username
    type: str
    required: true
  password:
    description:
      - Scale computing password
    type: str
    required: true
  uuid:
    description:
      - VM UUID
      - If included only VMs with matching UUID will be returned.
    type: str
"""

EXAMPLES = r"""
- name: Retrieve all VMs
  scale_computing.hc3.sample_vm_info:
  register: result

- name: Retrieve all VMs with specific name
  scale_computing.hc3.sample_vm_info:
    name: vm-a
  register: result
"""

RETURN = r"""
vms:
  description:
    - A list of VMs records.
  returned: success
  type: list
  sample:
    - name: "vm-name"
      uuid: "1234-0001"
      state: "running"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors
from ..module_utils.client import Client
from ..module_utils.utils import is_valid_uuid, get_nic_by_uuid


def check_parameters(module):
    if module.params["nic_uuid"] and not is_valid_uuid(module.params["nic_uuid"]):
        raise ValueError("Check UUID in playbook")


def run(module, client):
    check_parameters(module)

    end_point = "/rest/v1/VirDomainNetDevice"
    if module.params["nic_uuid"]:
        json_response = get_nic_by_uuid(client, module.params["nic_uuid"])
    else:
        json_response = client.request("GET", end_point).json

    return json_response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
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
            nic_uuid=dict(
                type="str",
            ),
        ),
        # we plan to identify VM by name (maybe UUID), NIC by vlan.
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
        # We do not want to just show complete API response to end user.
        # Because API response content changes with HC3 version.
        module.exit_json(changed=False, vms=vms)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
