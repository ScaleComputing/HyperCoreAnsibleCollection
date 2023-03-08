#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: support_tunnel

author:
  - Polona Mihalič (@PolonaM)
short_description:  Opens or closes remote support tunnel.
description:
  - Opens or closes remote support tunnel on the node.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  state:
    description:
      - The desired state of the remote support tunnel.
      - If C(state) is I(absent) the remote support tunnel will be closed.
      - If C(state) is I(present) the remote support tunnel will be opened.
    type: str
    choices: [ present, absent ]
    required: true
  code:
    description:
      - Code from support used to open remote support tunnel.
      - Relevant only if C(state) is I(present).
    type: int
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Open support tunnel
  scale_computing.hypercore.support_tunnel:
    state: present
    code: 4422

- name: Close support tunnel
  scale_computing.hypercore.support_tunnel:
    state: absent
"""

RETURN = r"""
record:
  description:
    - Support tunnel status.
  returned: success
  type: dict
  sample:
    - open: true
      code: 4422
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.typed_classes import TypedSupportTunnelToAnsible, TypedDiff
from ..module_utils.support_tunnel import SupportTunnel

# validate-modules does not agree with "from __future__ import annotations"
from typing import Tuple


def open_tunnel(
    module: AnsibleModule, client: Client
) -> Tuple[bool, TypedSupportTunnelToAnsible, TypedDiff]:
    tunnel_status = SupportTunnel.check_tunnel_status(client)
    if tunnel_status.open:  # if tunnel already opened
        if tunnel_status.code == module.params["code"]:
            return (
                False,
                tunnel_status.to_ansible(),
                dict(
                    before=tunnel_status.to_ansible(), after=tunnel_status.to_ansible()
                ),
            )
        else:
            SupportTunnel.close_tunnel(client)
    SupportTunnel.open_tunnel(module, client)
    new_tunnel_status = SupportTunnel.check_tunnel_status(client)
    if new_tunnel_status.open is False:
        raise errors.SupportTunnelError(
            "Support tunnel can't be opened, probably the code is already in use."
        )
    return (
        True,
        new_tunnel_status.to_ansible(),
        dict(before=tunnel_status.to_ansible(), after=new_tunnel_status.to_ansible()),
    )


def close_tunnel(
    client: Client,
) -> Tuple[bool, TypedSupportTunnelToAnsible, TypedDiff]:
    tunnel_status = SupportTunnel.check_tunnel_status(client)
    if not tunnel_status.open:  # if tunnel already closed
        return (
            False,
            tunnel_status.to_ansible(),
            dict(before=tunnel_status.to_ansible(), after=tunnel_status.to_ansible()),
        )
    SupportTunnel.close_tunnel(client)
    new_tunnel_status = SupportTunnel.check_tunnel_status(client)
    return (
        True,
        new_tunnel_status.to_ansible(),
        dict(before=tunnel_status.to_ansible(), after=new_tunnel_status.to_ansible()),
    )


def run(
    module: AnsibleModule, client: Client
) -> Tuple[bool, TypedSupportTunnelToAnsible, TypedDiff]:
    if module.params["state"] == "present":
        return open_tunnel(module, client)
    else:
        return close_tunnel(client)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            code=dict(type="int"),
        ),
        required_if=[
            ("state", "present", ("code",)),
        ],
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
