#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: user

author:
  - Polona Mihalič (@PolonaM)
short_description: Creates, updates or deletes local hypercore user accounts.
description:
  - Creates, updates or deletes local hypercore user accounts.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.user_info
options:
  state:
    description:
      - The desired state of the user account.
      - Use C(absent) to ensure the user will be absent from the API and C(present) to ensure user will remain present on the API.
    type: str
    choices: [ present, absent ]
    required: true
  username:
    description:
      - The user name.
      - Serves as unique identifier.
      - If C(state) is I(present) and C(username) doesn't exist, a new user is created.
      - If C(state) is I(present) and C(username) already exists, existing user is updated.
      - If C(state) is I(absent) and C(username) is found, existing user is deleted.
    type: str
    required: True
  username_new:
    description:
      - New user name.
      - Relevant only if C(state) is I(present) and C(username) exists.
    type: str
  password:
    description:
      - Plain text password for authentication.
    type: str
  full_name:
    description:
      - Human-readable display name.
    type: str
  roles:
    description:
      - Names of the roles this user is a member of.
    type: list
    elements: str
    choices: [ Backup, VM Delete, Cluster Settings, Cluster Shutdown, VM Power Controls, Read, VM Create/Edit, Admin ]
  session_limit:
    description:
      - The maximum number of Sessions this user may have at one time.
    type: int
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Create new user
  scale_computing.hypercore.user:
    state: present
    username: user
    password: password
    full_name: User
    roles:
      - VM delete
      - VM Create/Edit
      - VM Power Controls
    session_limit: 0

- name: Update existing user
  scale_computing.hypercore.user:
    state: present
    username: username
    username_new: updated_username
    password: updated_password

- name: Delete the user
  scale_computing.hypercore.user:
    state: absent
    username: user
"""

RETURN = r"""
record:
  description:
    - User record.
  returned: success
  type: dict
  sample:
    full_name: xlab
    roles:
      - Admin
    session_limit: 0
    username: xlab
    uuid: 51e6d073-7566-4273-9196-58720117bd7f
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.rest_client import CachedRestClient
from ..module_utils.user import User
from ..module_utils.role import Role


def get_role_uuids(module, rest_client: RestClient):
    # CachedRestClient is beneficial here since we use for loop and make get requests to the same endpoint many times
    role_uuids = []
    for role_name in module.params["roles"]:
        role = Role.get_role_from_name(role_name, rest_client, must_exist=True)
        role_uuids.append(role.uuid)
    return role_uuids


def data_for_create_user(module, rest_client: RestClient):
    data = {}
    data["username"] = module.params[
        "username"
    ]  # For api only username is required - SHOULD WE MAKE OTHER PARAMETERS REQUIRED?
    if module.params["password"]:
        data["password"] = module.params["password"]
    if module.params["full_name"]:
        data["fullName"] = module.params["full_name"]
    if module.params["roles"]:
        data["roleUUIDs"] = get_role_uuids(module, rest_client)
    if module.params["session_limit"] is not None:
        data["sessionLimit"] = module.params["session_limit"]
    return data


def create_user(module, rest_client: RestClient):
    data = data_for_create_user(module, rest_client)
    user = User.create(rest_client, data).to_ansible(rest_client)
    return (
        True,
        user,
        dict(before={}, after=user),
    )


def data_for_update_user(module, rest_client: RestClient, user):
    data = {}
    if module.params["username_new"]:
        if user.username != module.params["username_new"]:
            data["username"] = module.params["username_new"]
    if module.params["password"]:
        data["password"] = module.params["password"]  # password isn't visible in GET
    if module.params["full_name"]:
        if user.full_name != module.params["full_name"]:
            data["fullName"] = module.params["full_name"]
    if module.params["roles"]:
        role_uuids = get_role_uuids(module, rest_client)
        if user.role_uuids != role_uuids:
            data["roleUUIDs"] = role_uuids
    if (
        module.params["session_limit"] is not None
    ):  # "is not None" needed to be able to write zero
        if user.session_limit != module.params["session_limit"]:
            data["sessionLimit"] = module.params["session_limit"]
    return data


def update_user(module, rest_client: RestClient, user):
    data = data_for_update_user(module, rest_client, user)
    if data:
        user.update(rest_client, data)
        user_after = User.get_user_from_uuid(
            user.uuid, rest_client, must_exist=True
        ).to_ansible(rest_client)
        user = user.to_ansible(rest_client)
        return (
            True,
            user_after,
            dict(before=user, after=user_after),
        )
    user = user.to_ansible(rest_client)
    return (
        False,
        user,
        dict(before=user, after=user),
    )


def delete_user(rest_client: RestClient, user):
    if not user:
        return False, dict(), dict(before={}, after={})
    user.delete(rest_client)
    return True, dict(), dict(before=user.to_ansible(rest_client), after={})


def run(module, rest_client: RestClient):
    user = User.get_user_from_username(
        module.params["username"], rest_client, must_exist=False
    )
    if module.params["state"] == "present":
        if user:
            return update_user(module, rest_client, user)
        else:
            return create_user(module, rest_client)
    if module.params["state"] == "absent":
        return delete_user(rest_client, user)


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            username=dict(type="str", required=True),
            username_new=dict(type="str"),
            password=dict(type="str", no_log=True),
            full_name=dict(type="str"),
            roles=dict(
                type="list",
                elements="str",
                choices=[
                    "Backup",
                    "VM Delete",
                    "Cluster Settings",
                    "Cluster Shutdown",
                    "VM Power Controls",
                    "Read",
                    "VM Create/Edit",
                    "Admin",
                ],
            ),
            session_limit=dict(type="int"),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = CachedRestClient(client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
