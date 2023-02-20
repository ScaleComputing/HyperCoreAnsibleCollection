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
shutdown:
  description: C(true) if the cluster has been shut down.
  returned: always
  type: bool
  sample: true
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.cluster import Cluster


def run(module: AnsibleModule, rest_client: RestClient) -> bool:
    Cluster.shutdown(rest_client, module.params["force_shutdown"])
    return True


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
        shutdown = run(module, rest_client)
        module.exit_json(shutdown=shutdown)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
