#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# language=yaml
DOCUMENTATION = r"""
module: node_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Returns information about the nodes in a cluster.
description:
  - Returns information about the nodes in a cluster.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.vm_node_affinity
"""

# language=yaml
EXAMPLES = r"""
- name: List all cluster nodes
  scale_computing.hypercore.node_info:
  register: nodes
"""

# language=yaml
RETURN = r"""
records:
  description:
    - A list of node records.
  returned: success
  type: list
  elements: dict
  contains:
    node_uuid:
      description: Unique identifier
      type: str
      sample: 51e6d073-7566-4273-9196-58720117bd7f
    backplane_ip:
      description: IP address on the backplane network
      type: str
      sample: 10.0.0.1
    lan_ip:
      description: IP address on the LAN network
      type: str
      sample: 10.0.0.2
    peer_id:
      description: Cluster map peer identifier
      type: str
      sample: 1
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.rest_client import RestClient
from ..module_utils.client import Client
from ..module_utils.node import Node


def run(rest_client):
    return [
        Node.from_hypercore(hypercore_data=hypercore_dict).to_ansible()
        for hypercore_dict in rest_client.list_records("/rest/v1/Node")
    ]


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(arguments.get_spec("cluster_instance")),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        records = run(rest_client)
        module.exit_json(changed=False, records=records)

    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
