#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: cluster_shutdown

author:
  - Polona Mihalič (@PolonaM)
short_description: Shutdown cluster.
description:
  - Shutdown cluster.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  force_shutdown:
      description:
        - Bypasses attempts to gracefully shut down all runnning VirDomains before system shutdown.
        - Defaults to false.
      type: bool
      default: false
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Shutdown cluster
  scale_computing.hypercore.cluster_shutdown:
    force_shutdown: true
"""

RETURN = r"""
record:
  description:
    - Cluster that was shutdown.
  returned: success
  type: dict
  sample:
    - icos_version: 9.2.11.210763
      name: PUB5
      uuid: a5d9148c-37f7-4b43-843c-196751d3c050
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.cluster import Cluster
from ..module_utils.typed_classes import TypedDiff
from typing import Tuple, Dict


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Dict[None, None], TypedDiff]:
    cluster = Cluster.get(rest_client)
    Cluster.shutdown(rest_client, module.params["force_shutdown"])
    return (
        True,
        dict(),
        dict(before=cluster.to_ansible(), after=None),
    )  # WHAT TO RETURN?


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            force_shutdown=dict(type="bool", default=False),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        record = run(module, rest_client)
        module.exit_json(record=record)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
