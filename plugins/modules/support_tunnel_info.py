#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: support_tunnel_info

author:
  - Polona Mihalič (@PolonaM)
short_description:  Checks status of the remote support tunnel.
description:
  - Checks status of the remote support tunnel on the node.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
"""

EXAMPLES = r"""
- name: Check status of the remote support tunnel
  scale_computing.hypercore.support_tunnel_info:
"""

RETURN = r"""
record:
  description:
    - Support tunnel status.
  returned: success
  type: dict
  sample:
    open: true
    code: 4422
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.typed_classes import TypedSupportTunnelToAnsible
from ..module_utils.support_tunnel import SupportTunnel


def run(client: Client) -> TypedSupportTunnelToAnsible:
    return SupportTunnel.check_tunnel_status(client).to_ansible()


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        record = run(client)
        module.exit_json(record=record)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
