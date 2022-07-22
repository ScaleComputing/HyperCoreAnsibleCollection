#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: sample_vm_info

author:
  - First Second (@firstsecond)
short_description: Sample plugin
description:
  - A sample plugin with boilerplate code.
version_added: 0.0.1
extends_documentation_fragment: []
seealso: []
options:
  name:
    description:
      - VM name
      - If included only VMs with matching name will be returned.
    type: str
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


def run(module, client):
    # Use client to get info about all VMs.
    vm_all = [
        {
            "name": "vm-a",
            "uuid": "1234-0001",
            "state": "running",
        },
        {
            "name": "vm-b",
            "uuid": "1234-0002",
            "state": "stopped",
        },
    ]
    # Filter response if user wants only one VM.
    for filter_key in ["name", "uuid"]:
        if module.params.get(filter_key):
            filter_value = module.params.get(filter_key)
            vm_all = [vm for vm in vm_all if filter_value == vm[filter_key]]
    return vm_all


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            name=dict(),
            uuid=dict(),
        ),
        mutually_exclusive=[
            ("name", "uuid"),
        ],
    )

    try:
        client = Client()
        vms = run(module, client)
        module.exit_json(changed=False, vms=vms)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
