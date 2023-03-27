#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: oidc_config_info

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Returns information about openID connect configuration.
description:
  - Can list openID connect configuration.
  - One openID connect configuration per cluster is supported.
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
"""

EXAMPLES = r"""
- name: info OIDC config
  scale_computing.hypercore.oidc_config_info:
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
from ..module_utils.client import Client
from ..module_utils.oidc import Oidc
from ..module_utils.rest_client import CachedRestClient
from ..module_utils.typed_classes import TypedOidcToAnsible
from typing import Union, Tuple


def run(
    module: AnsibleModule, rest_client: CachedRestClient
) -> Tuple[bool, Union[TypedOidcToAnsible, None]]:
    oidc_list = rest_client.list_records("/rest/v1/OIDCConfig")
    if oidc_list:
        return False, Oidc.from_hypercore(oidc_list[0]).to_ansible()
    return False, None


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = CachedRestClient(client=client)
        changed, record = run(module, rest_client)
        module.exit_json(changed=changed, record=record)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
