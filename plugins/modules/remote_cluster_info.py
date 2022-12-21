#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: remote_cluster_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Retrieve a list of remote clusters.
description:
  - Retrieve a list of remote clusters from the HyperCore API endpoint C(/rest/v1/RemoteClusterConnection).
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.vm_replication
  - module: scale_computing.hypercore.snapshot_schedule
options:
  remote_cluster:
    type: str
    description:
      - Remote cluster's name.
      - If specified, the remote cluster with that specific name will get returned.
      - Otherwise, all remote clusters are going to get listed.
"""

EXAMPLES = r"""
- name: Get info about specific remote cluster
  scale_computing.hypercore.remote_cluster_info:
    remote_cluster: PUB4
  register: result

- name: Get info about all remote clusters
  scale_computing.hypercore.remote_cluster_info:
  register: result
"""

RETURN = r"""
records:
  description:
    - A list of remote cluster records.
  returned: success
  type: list
  sample:
    - name: PUB4
      connection_status: established
      replication_ok: True
      remote_node_ips:
        - 10.5.11.11
      remote_node_uuids:
        - 0000-0000
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.rest_client import RestClient
from ..module_utils.utils import filter_results
from ..module_utils.client import Client
from ..module_utils.remote_cluster import RemoteCluster


def run(module, rest_client):
    records = [
        RemoteCluster.from_hypercore(remote_cluster_dict=hypercore_dict).to_ansible()
        for hypercore_dict in rest_client.list_records(
            "/rest/v1/RemoteClusterConnection"
        )
    ]
    # Since get_query doesn't work for nested parameters (name -> remoteClusterInfo.clusterName) we have this workaround
    # In case of additional modules needing this functionality, get_query (and is_superset()) will have to be updated
    if module.params["remote_cluster"]:
        ansible_query = dict(name=module.params["remote_cluster"])
    else:
        ansible_query = {}
    return filter_results(records, ansible_query)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            remote_cluster=dict(
                type="str",
                required=False,
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)

    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
