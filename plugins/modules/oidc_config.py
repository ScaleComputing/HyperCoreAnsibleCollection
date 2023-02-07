#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: oidc_config

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Handles openID connect configuration.
description:
  - Can create, update or delete openID connect configuration.
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the openID connect configuration.
    choices: [ present, absent ]
    type: str
    required: True
  client_id:
    description:
      - Provided by authentication server when configuring a new client.
    type: str
  shared_secret:
    description:
      - Provided by authentication server for client authentication.
      - Write only.
    type: str
  certificate:
    description:
      - Plain text of the X.509 PEM-encode certificate.
    type: str
  config_url:
    description:
      - The openID connect provider configuration information endpoint.
    type: str
    required: true
  scopes:
    description:
      - Scopes required to obtain necessary claims.
    type: str
    required: true
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: New OIDC config
  scale_computing.hypercore.oidc_config:
    client_id: 12345
    shared_secret: secret_stuff
    certificate: plain_text_from_x509
    config_url: https:somwhere.com/this/endpoint
    scopes: required_scopes
    state: present
"""

RETURN = r"""
record:
  description:
    - OIDC config record.
  returned: success
  type: dict
  sample:
    client_ID: 1234
    certificate: this_certificate
    config_url: https://somewhere.com/this/endpoint
    scopes: required_scopes
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
from typing import Union, Tuple


def ensure_present(
    module: AnsibleModule,
    rest_client: RestClient,
    registration_obj: Union[Registration, None],
) -> Tuple[bool, Union[TypedRegistrationToAnsible, None], TypedDiff, bool]:
    return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(
    module: AnsibleModule,
    rest_client: RestClient,
    registration_obj: Union[Registration, None],
) -> Tuple[bool, Union[TypedRegistrationToAnsible, None], TypedDiff, bool]:
    return is_changed(before, after), after, dict(before=before, after=after)


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedRegistrationToAnsible, None], TypedDiff, bool]:
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
            client_id=dict(
                type="str",
            ),
            shared_secret=dict(
                type="str",
            ),
            certificate=dict(
                type="str",
            ),
            config_url=dict(
                type="str",
                required=True
            ),
            scopes=dict(
                type="str",
                required=True
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
