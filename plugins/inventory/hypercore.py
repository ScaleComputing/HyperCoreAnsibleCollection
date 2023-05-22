# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: hypercore
author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Inventory source for Scale Computing HyperCore.
description:
  - Builds an inventory containing VMs on Scale Computing HyperCore.
  - Inventory uses tags to group VMs and to add variables to inventory.
  - VM can be added to multiple groups.
  - Available tags - ansible_host__, ansible_group__, ansible_user__, ansible_port__, ansible_ssh_private_key_file__.
  - Does not support caching.
version_added: 1.0.0
seealso: []
options:
  plugin:
    description:
      - The name of the Hypercore Inventory Plugin.
      - This should always be C(scale_computing.hypercore.hypercore).
    required: true
    type: str
    choices: [ scale_computing.hypercore.hypercore ]
  look_for_ansible_enable:
    description:
      - If missing, all VMs are included into inventory.
      - If set, then only VMs with "ansible_enable" tag are included into inventory.
    type: bool
    default: false
    required: false
  look_for_ansible_disable:
    description:
      - If missing, no VMs are excluded into inventory.
      - If set, then VMs with "ansible_disable" tag are not included into inventory.
    type: bool
    default: false
    required: false
"""
EXAMPLES = r"""
# A trivial example that creates a list of all VMs.
# No groups will be created - all the resulting hosts are ungrouped.

plugin: scale_computing.hypercore.hypercore

# `ansible-inventory -i examples/hypercore_inventory.yaml --graph` output:
#@all:
#  |--@grp0:
#  |  |--ci-inventory-vm4
#  |  |--ci-inventory-vm6
#  |--@grp1:
#  |  |--ci-inventory-vm5
#  |  |--ci-inventory-vm6
#  |--@ungrouped:
#  |  |--ci-inventory-vm2
#  |  |--ci-inventory-vm3


# Example with all available parameters and how to set them.
# A group "my-group" is created where all the VMs with "ansbile_enable" tag are added.
# For VM "ci-inventory-vm6" we added values for host and user, every other VM has default values.

plugin: scale_computing.hypercore.hypercore

look_for_ansible_enable: True
look_for_ansible_disable: True

# `ansible-inventory -i hypercore_inventory.yaml --list` output:
#{
#    "_meta": {
#        "hostvars": {
#            "ci-inventory-vm2": {
#                "ansible_host": "10.0.0.2",
#               "ansible_port": 22,
#                "ansible_user": "root"
#            },
#            "ci-inventory-vm3": {
#               "ansible_host": "10.0.0.3",
#               "ansible_port": 22,
#               "ansible_user": "root"
#            },
#            "ci-inventory-vm4": {
#               "ansible_host": "10.0.0.4",
#               "ansible_port": 22,
#               "ansible_user": "root"
#            },
#            "ci-inventory-vm5": {
#               "ansible_host": "ci-inventory-vm5",
#               "ansible_port": 22,
#               "ansible_user": "root"
#            },
#            "ci-inventory-vm6": {
#               "ansible_host": "ci-inventory-vm6",
#               "ansible_port": 22,
#               "ansible_user": "root"
#           }
#       }
#    },
#    "all": {
#        "children": [
#           "grp0",
#           "grp1",
#           "ungrouped"
#        ]
#    },
#   "grp0": {
#        "hosts": [
#           "ci-inventory-vm4",
#           "ci-inventory-vm6"
#        ]
#   },
#    "grp1": {
#        "hosts": [
#            "ci-inventory-vm5",
#            "ci-inventory-vm6"
#        ]
#    },
#    "ungrouped": {
#        "hosts": [
#            "ci-inventory-vm2",
#           "ci-inventory-vm3"
#        ]
#   }
#}


"""
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
import yaml
import logging
from ..module_utils import errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
import os

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class LdapBaseException(Exception):
    pass


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = "hypercore"  # used internally by Ansible, it should match the file name but not required

    @classmethod
    def read_config_data(cls, path, env):
        """
        Reads and validates the inventory source file and environ,
        storing the provided configuration as options.
        """
        with open(path, "r") as inventory_src:
            cfg = yaml.safe_load(inventory_src)
        return cfg

    @classmethod
    def add_user(cls, inventory, ansible_user, vm_name):
        if ansible_user:
            inventory.set_variable(vm_name, "ansible_user", ansible_user)
        else:
            # we set "root" as default user
            inventory.set_variable(vm_name, "ansible_user", "root")
        return inventory

    @classmethod
    def add_port(cls, inventory, ansible_port, vm_name):
        if ansible_port:
            inventory.set_variable(vm_name, "ansible_port", ansible_port)
        else:  # default is 22
            inventory.set_variable(vm_name, "ansible_port", 22)
        return inventory

    @classmethod
    def add_group(cls, inventory, groups, vm_name):
        if len(groups) > 0:
            for group in groups:
                inventory.add_group(group)
                inventory.add_host(vm_name, group=group)
        else:
            inventory.add_host(vm_name, group=None)
        return inventory

    @classmethod
    def add_host(cls, inventory, ansible_host, vm_name):
        inventory.set_variable(vm_name, "ansible_host", ansible_host)
        return inventory

    @classmethod
    def add_ssh_private_key_file(cls, inventory, ansible_ssh_private_key_file, vm_name):
        if ansible_ssh_private_key_file:
            inventory.set_variable(
                vm_name, "ansible_ssh_private_key_file", ansible_ssh_private_key_file
            )
        return inventory

    def verify_file(self, path):
        """
        return true/false if this is possibly a valid file for this plugin to consume
        """
        # only check file is yaml, and contains magic plugin key with correct value.
        with open(path, "r") as inventory_src:
            config_contents = yaml.safe_load(inventory_src)
        plugin = config_contents.get("plugin")
        if not plugin:
            return False
        if plugin not in [self.NAME, "scale_computing.hypercore.hypercore"]:
            return False
        return True

    def parse(self, inventory, loader, path, cache=False):
        super(InventoryModule, self).parse(inventory, loader, path)
        cfg = self.read_config_data(path, os.environ)

        # get variables from env
        host = os.getenv("SC_HOST")
        username = os.getenv("SC_USERNAME")
        password = os.getenv("SC_PASSWORD")
        timeout = os.getenv("SC_TIMEOUT")
        auth_method = os.getenv("SC_AUTH_METHOD")
        if timeout:
            try:
                timeout = float(timeout)
            except ValueError:  # "could not convert string to float"
                raise errors.ScaleComputingError(
                    f'Environ variable "SC_TIMEOUT" has invalid value {timeout}. The value cannot be converted to number'
                )
        if host is None or username is None or password is None:
            raise errors.ScaleComputingError(
                "Missing one or more parameters: sc_host, sc_username, sc_password."
            )
        client = Client(host, username, password, timeout, auth_method)
        rest_client = RestClient(client)
        vms = rest_client.list_records("/rest/v1/VirDomain")

        for vm in vms:
            groups = []
            ansible_user = None
            ansible_port = None
            ansible_ssh_private_key_file = None
            include = True
            tags = vm["tags"].split(",")
            if (
                "look_for_ansible_enable" in cfg
                and cfg["look_for_ansible_enable"]
                and "look_for_ansible_disable" in cfg
                and cfg["look_for_ansible_disable"]
            ):
                include = False
                if "ansible_enable" in tags:
                    include = True
                if "ansible_disable" in tags:
                    include = False
            elif "look_for_ansible_enable" in cfg and cfg["look_for_ansible_enable"]:
                include = False
                if "ansible_enable" in tags:
                    include = True
            elif "look_for_ansible_disable" in cfg and cfg["look_for_ansible_disable"]:
                include = True
                if "ansible_disable" in tags:
                    include = False
            for tag in tags:
                if (
                    tag.startswith("ansible_group__")
                    and tag[len("ansible_group__"):] not in groups
                ):
                    groups.append(tag[len("ansible_group__"):])
                elif tag.startswith("ansible_user__"):
                    ansible_user = tag[len("ansible_user__"):]
                elif tag.startswith("ansible_port__"):
                    ansible_port = int(tag[len("ansible_port__"):])
                elif tag.startswith("ansible_ssh_private_key_file"):
                    ansible_ssh_private_key_file = tag[
                        len("ansible_ssh_private_key_file__"):
                    ]
            if include:
                # Group
                inventory = self.add_group(inventory, groups, vm["name"])
                ansible_host = vm["name"]
                # Find ansible_host
                # For time being, just use the very first IP address.
                # Later - get smarter. Use IP address from specific VLAN maybe.
                # But end user is always most smart - use tag ansible_host if it is set;
                # this will allow use of arbitrary IP or even DNS name.
                for nic in vm["netDevs"]:
                    if nic["ipv4Addresses"]:
                        ansible_host = nic["ipv4Addresses"][0]
                        break
                for tag in tags:
                    if tag.startswith("ansible_host__"):
                        ansible_host = tag[len("ansible_host__"):]
                # User
                inventory = self.add_user(inventory, ansible_user, vm["name"])
                # Port
                inventory = self.add_port(inventory, ansible_port, vm["name"])
                # Host
                inventory = self.add_host(inventory, ansible_host, vm["name"])
                # SSH private key file
                inventory = self.add_ssh_private_key_file(
                    inventory, ansible_ssh_private_key_file, vm["name"]
                )
