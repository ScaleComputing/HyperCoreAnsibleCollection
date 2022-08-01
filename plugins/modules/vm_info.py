#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_info

author:
  - Domen Dobnikar (@domen_dobnikar)
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
    host: 'Host IP address'
    username: 'Your scale cluster username'
    password: 'Your scale cluster password'
  register: result

- name: Retrieve all VMs with specific UUID
  scale_computing.hc3.sample_vm_info:
    host: 'Host IP address'
    username: 'Your scale cluster username'
    password: 'Your scale cluster password'
    uuid: 'valid virtual machine UUID'
  register: result
"""

RETURN = r"""
vms:
  description:
    - A list of VMs records.
  returned: success
  type: list
  sample:
    - "boot_devices": 
            - "name": ""
              "slot": 0,
              "type": "disk",
              "uuid": "fec11a1d-e8e3-4a50-8b50-57dece3e8baf"
      "cloud_init": {
              "metadata": ""
              "userdata": ""
      "description": "XLAB-ac1-export-20220705T201528: "
      "disks":
            - "capacity": "8 GB"
              "name": ""
              "slot": 0
              "type": "VIRTIO_DISK"
              "uuid": "e8c8aa6b-1043-48a0-8407-2c432d705378"
              "mem": "488 MB"
      "name": "XLAB-CentOS-7-x86_64-GenericCloud-2111"
      "nics":
            - "type": "RTL8139",
              "uuid": "4c627449-99c6-475b-8e8e-9ae2587db5fc"
              "vlan": 0
      "numVCPU": 2
      "state": "SHUTOFF"
      "tags": "Xlab,ac1,us3",
      "uuid": "f0c91f97-cbfc-40f8-b918-ab77ae8ea7fb"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors
from ..module_utils.client import Client
from ..module_utils.utils import is_valid_uuid


def value_from_B_to_MB(value):
    return str(round(value / 1048576))


def value_from_B_to_GB(value):
    return str(round(value / 1073741824))


def find_boot_device(all_device_dict, boot_device_list):
    boot_device_info_list = []
    for device_uuid in all_device_dict.keys():
        if device_uuid in boot_device_list:
            boot_device_info_list.append(all_device_dict[device_uuid])
    return boot_device_info_list


def create_disk_info_list(disk_data_list):
    disk_info_list = []
    for disk in disk_data_list:
        virtual_machine_disk_info_dict = {}
        virtual_machine_disk_info_dict["uuid"] = disk["uuid"]
        virtual_machine_disk_info_dict["slot"] = disk["slot"]
        virtual_machine_disk_info_dict["name"] = disk["name"]
        # will we use capacity or size?
        # with unit GB/MB or without unit (so it is bytes, always)?
        virtual_machine_disk_info_dict["capacity"] = (
            value_from_B_to_GB(disk["capacity"]) + " GB"
        )
        virtual_machine_disk_info_dict["type"] = disk["type"]
        disk_info_list.append(virtual_machine_disk_info_dict)
    return disk_info_list


def create_network_interface_info_list(network_interface_data_list):
    network_interface_info_list = []
    for network_interface in network_interface_data_list:
        virtual_machine_nic_info_dict = {}
        virtual_machine_nic_info_dict["uuid"] = network_interface["uuid"]
        virtual_machine_nic_info_dict["vlan"] = network_interface["vlan"]
        virtual_machine_nic_info_dict["type"] = network_interface["type"]
        network_interface_info_list.append(virtual_machine_nic_info_dict)
    return network_interface_info_list


def create_all_device_info_dict(all_device_dict):
    all_device_info_dict = {}

    for disk in all_device_dict["blockDevs"]:
        all_device_info_dict[disk["uuid"]] = {
            "type": "disk",
            "name": disk["name"],
            "slot": disk["slot"],
            "uuid": disk["uuid"],
        }
    for network_interface in all_device_dict["netDevs"]:
        all_device_info_dict[network_interface["uuid"]] = {
            "type": "nic",
            "vlan": network_interface["vlan"],
            "uuid": network_interface["uuid"],
        }

    return all_device_info_dict


def create_vm_info_list(json_data):
    virtual_machines_info_list = []
    for virtual_machine_info in json_data:
        virtual_machine_info_dict = {}
        virtual_machine_info_dict["uuid"] = virtual_machine_info["uuid"]
        virtual_machine_info_dict["name"] = virtual_machine_info["name"]
        virtual_machine_info_dict["description"] = virtual_machine_info["description"]
        virtual_machine_info_dict["memory"] = (
            value_from_B_to_MB(virtual_machine_info["mem"]) + " MB"
        )
        virtual_machine_info_dict["state"] = virtual_machine_info["state"]
        virtual_machine_info_dict["numVCPU"] = virtual_machine_info["numVCPU"]
        virtual_machine_info_dict["tags"] = virtual_machine_info["tags"]

        virtual_machine_info_dict["disks"] = create_disk_info_list(
            virtual_machine_info["blockDevs"]
        )
        virtual_machine_info_dict["nics"] = create_network_interface_info_list(
            virtual_machine_info["netDevs"]
        )
        all_device_dict = create_all_device_info_dict(virtual_machine_info)

        boot_devices = find_boot_device(
            all_device_dict, virtual_machine_info["bootDevices"]
        )
        virtual_machine_info_dict["boot_devices"] = boot_devices

        # HC3 does not report cloudInitData in GET response.
        # We should drop it in vm_info too?
        virtual_machine_info_dict["cloud_init"] = {
            "userdata": virtual_machine_info["cloudInitData"]["userData"],
            "metadata": virtual_machine_info["cloudInitData"]["metaData"],
        }

        virtual_machines_info_list.append(virtual_machine_info_dict)
    return virtual_machines_info_list


def run(module, client):
    end_point = "/rest/v1/VirDomain"
    if module.params["uuid"] and is_valid_uuid(module.params["uuid"]):
        end_point += "/" + module.params["uuid"]

    json_response = client.request("GET", end_point).json

    virtual_machine_info_list = create_vm_info_list(json_response)

    return virtual_machine_info_list


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            host=dict(
                type="str",
                required=True,
            ),
            username=dict(
                type="str",
                required=True,
            ),
            password=dict(
                type="str",
                required=True,
            ),
            uuid=dict(type="str"),
            # we want/need to search for VM by name (and/or UUID).
        ),
        mutually_exclusive=[
            ("uuid"),  # uuid and name?
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
