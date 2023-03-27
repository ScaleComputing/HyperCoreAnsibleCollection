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
  - Can create or update openID connect configuration.
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  client_id:
    description:
      - Provided by authentication server when configuring a new client.
    type: str
    required: True
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
  - Module is not idempotent, it will always report changed=True.
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: New OIDC config
  scale_computing.hypercore.oidc_config:
    client_id: 12345
    shared_secret: secret_stuff
    certificate: plain_text_from_x509
    config_url: https://login.microsoftonline.com/your_uuid/v2.0/.well-known/openid-configuration
    scopes: "openid+profile"
"""

RETURN = r"""
record:
  description:
    - OIDC config record.
  returned: success
  type: dict
  contains:
    client_id:
      description: Provided by authentication server when configuring a new client
      type: str
      sample: d2298ec0-0596-49d2-9554-840a2fe20603
    config_url:
      description: The OpenID Connect Provider Configuration Information endpoint
      type: str
      sample: https://login.microsoftonline.com/your_uuid/v2.0/.well-known/openid-configuration
    scopes:
      description: Scopes required to obtain necessary claims
      type: str
      sample: openid+profile
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.errors import UnexpectedAPIResponse
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.oidc import Oidc
from ..module_utils.typed_classes import TypedOidcToAnsible, TypedDiff
from ..module_utils.task_tag import TaskTag
from typing import Tuple, Optional
from time import sleep


def ensure_present(
    module: AnsibleModule,
    rest_client: RestClient,
) -> Tuple[bool, Optional[TypedOidcToAnsible], TypedDiff]:
    oidc_obj_ansible = Oidc.from_ansible(module.params)
    # If we get "502 bad gateway" during reconfiguration, we need to retry.
    max_retries = 10
    for ii in range(max_retries):
        try:
            oidc_obj = Oidc.get(rest_client)
            before = oidc_obj.to_ansible() if oidc_obj else None
            if oidc_obj is None:
                task = oidc_obj_ansible.send_create_request(rest_client)
            else:
                task = oidc_obj_ansible.send_update_request(rest_client)
            TaskTag.wait_task(rest_client, task)
            break
        except UnexpectedAPIResponse as ex:
            if ex.response_status in [500, 502]:
                module.warn(
                    f"API misbehaving during reconfiguration, retry {ii+1}/{max_retries}"
                )
                sleep(1)
                continue
            else:
                raise
    updated_oidc = Oidc.get(rest_client)
    after = updated_oidc.to_ansible() if updated_oidc else None
    # We always sent POST or PATCH, so it is always changed=True
    return True, after, dict(before=before, after=after)


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[TypedOidcToAnsible], TypedDiff]:
    return ensure_present(module, rest_client)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            client_id=dict(
                type="str",
                required=True,
            ),
            shared_secret=dict(
                type="str",
                no_log=True,
            ),
            certificate=dict(
                type="str",
                no_log=True,
            ),
            config_url=dict(type="str", required=True),
            scopes=dict(type="str", required=True),
        ),
        required_one_of=[
            (
                "certificate",
                "shared_secret",
            ),
        ],
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
