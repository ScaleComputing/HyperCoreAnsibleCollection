#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: cluster_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Retrieve cluster info.
description:
  - Retrieve cluster's uuid, name and icos version from the HyperCore API endpoint C(/rest/v1/Cluster).
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.cluster_name
"""

EXAMPLES = r"""
- name: Get cluster info
  scale_computing.hypercore.cluster_info:
  register: result
"""

RETURN = r"""
record:
  description:
    - Cluster info.
  returned: success
  type: dict
  contains:
    icos_version:
      description: HyperCore ICOS version
      type: str
      sample: 9.2.11.210763
    name:
      description: Cluster name
      type: str
      sample: PUB4
    uuid:
      description: Cluster UUID
      type: str
      sample: a5d9148c-37f7-4b43-843c-196751d3c050
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.rest_client import RestClient
from ..module_utils.client import Client
from ..module_utils.cluster import Cluster
from ..module_utils.typed_classes import TypedClusterToAnsible


def run(rest_client: RestClient) -> TypedClusterToAnsible:
    record = Cluster.get(rest_client).to_ansible()
    return record


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        record = run(rest_client)
        module.exit_json(changed=False, record=record)

    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
