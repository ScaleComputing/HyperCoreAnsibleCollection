#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: user_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Returns information about the users.
description:
  - Returns information about the users.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.user
"""

EXAMPLES = r"""
- name: List all users
  scale_computing.hypercore.user_info:
  register: users
"""

RETURN = r"""
records:
  description:
    - A list of user records.
  returned: success
  type: list
  sample:
    - fullname: xlab
      role_uuids:
        - 38b346c6-a626-444b-b6ab-92ecd671afc0
        - 7224a2bd-5a08-4b99-a0de-9977089c66a4
      session_limit: 0
      username: xlab
      uuid: 51e6d073-7566-4273-9196-58720117bd7f
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.rest_client import RestClient
from ..module_utils.client import Client
from ..module_utils.user import User


def run(rest_client):
    return [
        User.from_hypercore(user_dict=hypercore_dict).to_ansible()
        for hypercore_dict in rest_client.list_records("/rest/v1/User")
    ]


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(arguments.get_spec("cluster_instance")),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        records = run(rest_client)
        module.exit_json(changed=False, records=records)

    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
