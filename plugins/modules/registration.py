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
  - Can create, update or delete cluster registration.
  - A single registration per cluster.
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the registration.
    choices: [ present, absent ]
    type: str
    required: True
  company_name:
    description:
      - Name of the company registering the cluster.
    type: str
  contact:
    description:
      - Name of the person registering the cluster.
    type: str
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
    contact: Janez Novak
    state: present

- name: Delete registration
  scale_computing.hypercore.registration:
    state: absent
"""

RETURN = r"""
record:
  description:
    - Registration record.
  returned: success
  type: dict
  contains:
    company_name:
      description: Name of the company registering the cluster
      type: str
      sample: New company
    contact:
      description: Name of the person registering the cluster
      type: str
      sample: John Smith
    email:
      description: Email address for company contact
      type: str
      sample: john_smith@gmail.com
    phone:
      description: Phone number for company contact
      type: str
      sample: 056789987
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.utils import is_changed
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.state import State
from ..module_utils.registration import Registration
from ..module_utils.typed_classes import TypedRegistrationToAnsible, TypedDiff
from ..module_utils.task_tag import TaskTag
from typing import Tuple, Optional


def ensure_present(
    module: AnsibleModule,
    rest_client: RestClient,
    registration_obj: Optional[Registration],
) -> Tuple[bool, Optional[TypedRegistrationToAnsible], TypedDiff]:
    before = registration_obj.to_ansible() if registration_obj else None
    registration_obj_ansible = Registration.from_ansible(module.params)
    if registration_obj is None:
        # Create
        task = registration_obj_ansible.send_create_request(rest_client)
    else:
        # Update
        task = registration_obj_ansible.send_update_request(rest_client)
    TaskTag.wait_task(rest_client, task)
    updated_registration = Registration.get(rest_client)
    after = updated_registration.to_ansible() if updated_registration else None
    return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(
    module: AnsibleModule,
    rest_client: RestClient,
    registration_obj: Optional[Registration],
) -> Tuple[bool, Optional[TypedRegistrationToAnsible], TypedDiff]:
    before = registration_obj.to_ansible() if registration_obj else None
    after = None
    if registration_obj:
        task = registration_obj.send_delete_request(rest_client)
        TaskTag.wait_task(rest_client, task)
        updated_registration = Registration.get(rest_client)
        after = updated_registration.to_ansible() if updated_registration else None
    return is_changed(before, after), after, dict(before=before, after=after)


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[TypedRegistrationToAnsible], TypedDiff]:
    registration_obj = Registration.get(rest_client)
    if module.params["state"] == State.present:
        return ensure_present(module, rest_client, registration_obj)
    return ensure_absent(module, rest_client, registration_obj)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=[
                    "present",
                    "absent",
                ],
                required=True,
            ),
            company_name=dict(
                type="str",
            ),
            contact=dict(
                type="str",
            ),
            phone=dict(
                type="str",
            ),
            email=dict(
                type="str",
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client=client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
