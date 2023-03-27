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
options:
  username:
    description:
      - The user name.
      - Serves as unique identifier.
    type: str
"""

EXAMPLES = r"""
- name: List all users
  scale_computing.hypercore.user_info:
  register: users

- name: List selected user
  scale_computing.hypercore.user_info:
    username: my_username
  register: user
"""

RETURN = r"""
records:
  description:
    - A list of user records.
  returned: success
  type: list
  elements: dict
  contains:
    full_name:
      description: Human-readable display name
      type: str
      sample: xlab
    roles:
      description: Role identifiers this user is a member of
      type: list
      elements: dict
      sample:
        uuid: 38b346c6-a626-444b-b6ab-92ecd671afc0
        name: Admin
    session_limit:
      description: The maximum number of Sessions this user may have at one time
      type: int
      sample: 0
    username:
      description: Human-readable unique identifier for authentication
      type: str
      sample: xlab
    uuid:
      description: Unique identifier
      type: str
      sample: 51e6d073-7566-4273-9196-58720117bd7f
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.rest_client import RestClient
from ..module_utils.client import Client
from ..module_utils.user import User
from ..module_utils.utils import get_query
from ..module_utils.typed_classes import TypedUserToAnsible
from typing import List, Optional


def run(
    module: AnsibleModule, rest_client: RestClient
) -> List[Optional[TypedUserToAnsible]]:
    query = get_query(
        module.params, "username", ansible_hypercore_map=dict(username="username")
    )
    return [
        User.from_hypercore(hypercore_data=hypercore_dict).to_ansible(  # type: ignore
            rest_client
        )
        for hypercore_dict in rest_client.list_records("/rest/v1/User", query)
    ]


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"), username=dict(type="str")
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)

    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
