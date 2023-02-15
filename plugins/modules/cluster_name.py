#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: cluster_name

author:
  - Polona Mihalič (@PolonaM)
short_description: Update cluster name.
description:
  - Update cluster name.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.cluster_info
options:
  name_new:
      description:
        - Updated cluster name.
      type: str
      required: true
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Update cluster name
  scale_computing.hypercore.cluster_name:
    name_new: updated_cluster_name
  register: result
"""

RETURN = r"""
record:
  description:
    - Updated cluster name.
  returned: success
  type: dict
  sample:
    - icos_version: 9.2.11.210763
      name: updated_cluster_name
      uuid: a5d9148c-37f7-4b43-843c-196751d3c050
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.cluster import Cluster
from ..module_utils.task_tag import TaskTag
from ..module_utils.typed_classes import TypedClusterToAnsible, TypedDiff
from typing import Tuple
from ..module_utils.hypercore_version import (
    HyperCoreVersion,
)

HYPERCORE_VERSION_REQUIREMENTS = ">=9.1.9 <9.2.0 || >=9.2.10"


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, TypedClusterToAnsible, TypedDiff]:
    cluster = Cluster.get(rest_client)
    if cluster.name == module.params["name_new"]:
        return (
            False,
            cluster.to_ansible(),
            dict(before=cluster.to_ansible(), after=cluster.to_ansible()),
        )
    task_tag = cluster.update_name(rest_client, module.params["name_new"])
    TaskTag.wait_task(rest_client, task_tag)
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
            name_new=dict(type="str", required=True),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        hcversion = HyperCoreVersion(rest_client)
        if not hcversion.verify(HYPERCORE_VERSION_REQUIREMENTS):
            msg = f"HyperCore server version={hcversion.version} does not match required version {HYPERCORE_VERSION_REQUIREMENTS}"
            module.fail_json(msg=msg)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()