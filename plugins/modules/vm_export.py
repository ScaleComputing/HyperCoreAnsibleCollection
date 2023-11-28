#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_export

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Handles export of the virtual machine
description:
  - Use vm_export to export the virtual machine, to a specified location on a SMB server.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
  - scale_computing.hypercore.vm_name
seealso: []
options:
  smb:
    description:
      - SMB server, access and location data.
    type: dict
    required: true
    suboptions:
      server:
        type: str
        description:
          - Specified SMB server, where the selected virtual machine is to be exported to.
          - Has to be IP or DNS name.
        required: true
      path:
        type: str
        description:
          - Specified location on the SMB server, where the exported virtual machine is to be exported to.
          - It must start with '/'.
        required: true
      file_name:
        type: str
        description:
          - Specified xml file name.
          - If not specified, file name will be the same as directory name from the path parameter.
      username:
        type: str
        description:
          - Username.
        required: true
      password:
        type: str
        description:
          - Password.
        required: true
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Export VM to SMB
  scale_computing.hypercore.vm_export:
    vm_name: demo-vm
    smb:
      server: IP-or-DNS-name-of-SMB-server
      path: /share/path/to/vms/demo-vm-exported-v0
      file_name: my_file.xml
      username: user
      password: pass
  register: output
"""

RETURN = r"""
msg:
  description:
    - Return message.
  returned: success
  type: str
  sample: Virtual machine - VM-TEST - export complete.
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.vm import VM
from ..module_utils.task_tag import TaskTag


def run(module, rest_client):
    virtual_machine_obj = VM.get_or_fail(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )[0]
    try:
        task = virtual_machine_obj.export_vm(rest_client, module.params)
        TaskTag.wait_task(rest_client, task)
        task_status = TaskTag.get_task_status(rest_client, task)
        if task_status and task_status.get("state", "") == "COMPLETE":
            return (
                True,
                f"Virtual machine - {module.params['vm_name']} - export complete.",
            )
        raise errors.ScaleComputingError(
            f"There was a problem during export of {module.params['vm_name']}, export failed."
        )
    except TimeoutError as e:
        raise errors.ScaleComputingError(f"Request timed out: {e}")


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_name=dict(
                type="str",
                required=True,
            ),
            smb=dict(
                type="dict",
                required=True,
                options=dict(
                    server=dict(
                        type="str",
                        required=True,
                    ),
                    path=dict(
                        type="str",
                        required=True,
                    ),
                    file_name=dict(
                        type="str",
                    ),
                    username=dict(
                        type="str",
                        required=True,
                    ),
                    password=dict(
                        type="str",
                        no_log=True,
                        required=True,
                    ),
                ),
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client=client)
        changed, msg = run(module, rest_client)
        module.exit_json(changed=changed, msg=msg)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
