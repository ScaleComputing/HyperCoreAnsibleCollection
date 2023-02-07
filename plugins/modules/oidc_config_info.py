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
short_description: Returns information about openID connect configurations.
description:
  - Can list openID connect configurations.
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
notes:
  - C(check_mode) is not supported.
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
from ..module_utils.typed_classes import TypedRegistrationToAnsible, TypedDiff
from typing import Union, Tuple


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedRegistrationToAnsible, None], TypedDiff, bool]:
    return ensure_absent(module, rest_client, registration_obj)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
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
