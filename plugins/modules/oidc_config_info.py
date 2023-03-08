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
  sample:
    client_id: 1234
    config_url: https://somewhere.com/this/endpoint
    scopes: required_scopes
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.oidc import Oidc
from ..module_utils.rest_client import CachedRestClient
from ..module_utils.typed_classes import TypedOidcToAnsible
from typing import Tuple, Optional


def run(
    module: AnsibleModule, rest_client: CachedRestClient
) -> Tuple[bool, Optional[TypedOidcToAnsible]]:
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
