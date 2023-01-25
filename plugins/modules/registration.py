#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: registration

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Handles cluster registration.
description:
  - Can create, update or delete cluster registrations.
  - A single registration can be identified by: I(company_name) and I(contact)
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  state:
    description:
      - State defines which operation should plugin do over selected registration.
    choices: [ present, absent ]
    type: str
    required: True
  company_name:
    description:
      - Name of the company registering the cluster.
    type: str
    required: True
  contact:
    description:
      - Name of the person registering the cluster.
    type: str
    required: True
  phone:
    description:
      - Phone number for company contact.
    type: str
  email:
    description:
      - Email address for company contact.
    type: str
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: New registration
  scale_computing.hypercore.registration:
    company_name: New company
    contact: John Smith
    phone: 056789987
    email: john_smith@gmail.com
    state: present
    
- name: Update registration
  scale_computing.hypercore.registration:
    company_name: New company
    contact: John Smith
    phone: 056789987
    email: john_smith@gmail.com
    state: present

- name: Delete registration
  scale_computing.hypercore.registration:
    company_name: New company
    contact: John Smith
    state: absent
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient




def run(module, rest_client):
    return changed, records, diff, reboot


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                required=True,
                choices=["present", "absent"],
            ),
            company_name=dict(
                type="str",
                required=True,
            ),
            contact=dict(
                type="str",
                required=True,
            ),
            phone=dict(
                type="str",
            ),
            email=dict(
                type="str",
            ),
        ),
        required_if=[
            (
                "state",
                "present",
                (
                    "phone",
                    "email",
                ),
                False,
            ),
        ],
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client=client)
        changed, records, diff, reboot = run(module, rest_client)
        module.exit_json(
            changed=changed, records=records, diff=diff, vm_rebooted=reboot
        )
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
