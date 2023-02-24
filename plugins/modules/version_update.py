#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: version_update

author:
  - Polona Mihalič (@PolonaM)
short_description: Install an update on the cluster.
description:
  - From available hypercore version updates install selected update on the cluster.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.version_update_info
  - module: scale_computing.hypercore.version_update_status_info
options:
  icos_version:
      description:
        - Hypercore version update to be installed on the cluster.
      type: str
      required: true
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Update hypercore version
  scale_computing.hypercore.version_update:
    icos_version: 9.2.11.210763
  register: result
"""

RETURN = r"""
record:
  description:
    - Cluster info.
  returned: success
  type: dict
  sample:
    - icos_version: 9.2.11.210763
      name: cluster_name
      uuid: a5d9148c-37f7-4b43-843c-196751d3c050
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.cluster import Cluster
from ..module_utils.hypercore_version import Update, UpdateStatus
from ..module_utils.typed_classes import TypedClusterToAnsible, TypedDiff
from typing import Tuple
from time import sleep


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, TypedClusterToAnsible, TypedDiff]:
    cluster = Cluster.get(rest_client)
    if cluster.icos_version == module.params["icos_version"]:
        return (
            False,
            cluster.to_ansible(),
            dict(before=cluster.to_ansible(), after=cluster.to_ansible()),
        )
    Update.apply(rest_client, module.params["icos_version"])
    while True:
        sleep(30)
        update_status = UpdateStatus.get(rest_client).status
        if update_status == "IN PROGRESS":
            pass
        elif update_status == "COMPLETE":
            break
        else:
            raise errors.UpdateNotSuccessfull
    cluster_updated = Cluster.get(rest_client)
    return (
        True,
        cluster_updated.to_ansible(),
        dict(before=cluster.to_ansible(), after=cluster_updated.to_ansible()),
    )


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            icos_version=dict(type="str", required=True),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
