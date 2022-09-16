#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_clone

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Plugin handles cloning of the virtual machine.
description:
  - Plugin enables cloning of the specified virtual machine.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  vm_name:
    description:
      - Virtual machine name.
      - Name of the clone.
      - Used to identify a virtual machine by name.
    type: str
    required: true
  source_vm_name:
    description:
      - Virtual machine name.
      - Name of the source virual machine, to be cloned.
      - Used to identify selected virtual machine by name.
    type: str
    required: true
  cloud_init:
    description:
      - Configuration to be used by cloud-init (Linux) or cloudbase-init (Windows).
      - When non-empty will create an extra ISO device attached to VirDomain as a NoCloud datasource.
      - There has to be cloud-config comment present at the beginning of cloud_init file or raw yaml.
    required: false
    type: dict
    suboptions:
      user_data:
        description:
          - Configuration user-data to be used by cloud-init (Linux) or cloudbase-init (Windows).
          - Valid YAML syntax.
        type: str
      meta_data:
        type: str
        description:
          - Configuration meta-data to be used by cloud-init (Linux) or cloudbase-init (Windows).
          - Valid YAML syntax.
  tags:
    description:
      - Virtual machine tags.
      - Used to group virtual machine.
    required: false
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Clone VM
  scale_computing.hypercore.vm_clone:
    vm_name: demo-vm-clone
    source_vm_name: demo-vm
    cloud_init:
      user_data: "{{ lookup('file', 'cloud-init-user-data-example.yml') }}"
      meta_data: |
        #cloud-config
        valid:
          yaml: 3
          expression: 4
    tags:
      - test
      - tag
  register: output
"""

RETURN = r"""
msg:
  description:
    - Return message.
  returned: success
  type: str
  sample: Virtual machine - VM-TEST - cloning complete to - VM-TEST-clone
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.task_tag import TaskTag


def run(module, rest_client):
    # Check if clone_vm already exists
    if VM.get(query={"name": module.params["vm_name"]}, rest_client=rest_client):
        return (
            False,
            f"Virtual machine {module.params['vm_name']} already exists.",
        )
    virtual_machine_obj = VM.get_or_fail(
        query={"name": module.params["source_vm_name"]}, rest_client=rest_client
    )[0]
    task = virtual_machine_obj.clone_vm(rest_client, module.params)
    TaskTag.wait_task(rest_client, task)
    task_status = TaskTag.get_task_status(rest_client, task)
    if task_status.get("state", "") == "COMPLETE":
        return (
            True,
            f"Virtual machine - {module.params['source_vm_name']} - cloning complete to - {module.params['vm_name']}.",
        )
    raise errors.ScaleComputingError(
        f"There was a problem during cloning of {module.params['source_vm_name']}, cloning failed."
    )


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            source_vm_name=dict(
                type="str",
                required=True,
            ),
            tags=dict(  # We give user a chance to add aditional tags here.
                type="list", elements="str"
            ),
            cloud_init=dict(
                type="dict",
                default={},
                options=dict(
                    user_data=dict(type="str"),
                    meta_data=dict(type="str"),
                ),
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        rest_client = RestClient(client=client)
        changed, msg = run(module, rest_client)
        module.exit_json(changed=changed, msg=msg)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
