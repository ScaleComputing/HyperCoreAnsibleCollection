#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_nic

author:
  - First Second (@firstsecond)
short_description: Sample plugin
description:
  - A sample plugin with boilerplate code.
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hc3.cluster_instance
seealso: []
options:
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

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.utils import is_valid_uuid, get_nic_by_uuid, wait_task, get_all_nics


def check_parameters(module):
    if not is_valid_uuid(module.params["virDomainUUID"]):
        raise ValueError("Check UUID in playbook")


def create_request_body(module, vm_uuid):
    request_body = module
    module.pop("nic_uuid", None)
    module["virDomainUUID"] = vm_uuid
    return request_body


def create_nic(module, client, end_point, vm_uuid):
    request_body = create_request_body(module, vm_uuid)
    json_response = client.request("POST", end_point, data=request_body).json
    return json_response


def update_nic(module, client, end_point, vm_uuid):
    request_body = create_request_body(module, vm_uuid)
    json_response = client.request("PATCH", end_point, data=request_body).json
    return json_response


def delete_nic(client, end_point):
    json_response = client.request("DELETE", end_point).json
    return json_response

def delete_not_used_nics(module, client, end_point):
    all_nics = get_all_nics(client)
    for nic in all_nics:
        if nic["virDomainUUID"] == module.params["virDomainUUID"] and nic["uuid"] not in module.params["nics"]:
            json_response = delete_nic(client, end_point + "/" + nic["nic_uuid"])
            wait_task(json_response, client)

def check_state_decide_action(state, module, client):
    end_point = "/rest/v1/VirDomainNetDevice"
    vm_uuid = module.params["virDomainUUID"]
    json_response = ""
    for nic in module.params["nics"]:
      if nic["nic_uuid"] and get_nic_by_uuid(client, nic["nic_uuid"]):
        if state == "PRESENT" or state == "SET":
          json_response = update_nic(nic, client, end_point + "/" + nic["nic_uuid"], vm_uuid)
        elif state == "ABSENT":
          json_response = delete_nic(client, end_point + "/" + nic["nic_uuid"])
      elif state == "PRESENT" or state == "SET":
        json_response = create_nic(nic, client, end_point, vm_uuid)  # isn't module first param to create_nic?
      wait_task(json_response, client)
    if state == "SET":
      delete_not_used_nics(module, client, end_point)
    return json_response


def run(module, client):
    check_parameters(module)

    json_response = check_state_decide_action(
        # that module.params["state"].upper() - upper() is not needed, possible states PRESENT|ABSENT|SET are not
        # from HC3, they are our invention.
        module.params["state"].upper(), module, client
    )

    return json_response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                required=True,
                choices=["PRESENT", "ABSENT", "SET"],
            ),
            virDomainUUID=dict(  # vm_uuid, vm_name, name?
                type="str",
                required=True,
            ),
            nics=dict(
                type="list",
                elements="dict",
            ),
        ),
        mutually_exclusive=[
            ("name", "uuid"),  # aha, name
        ],
    )

    try:
        url = module.params["cluster_instance"]["url"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]
        
        client = Client(url, username, password)
        vms = run(module, client)
        module.exit_json(changed=False, vms=vms)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
