#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type


# language=yaml
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
  force_update:
    description:
      - Upgrade the HyperCore cluster to the requested version,
        even if requested version is not listed under available versions of the HyperCore cluster.
    type: bool
    default: false
notes:
  - C(check_mode) is not supported.
"""

# language=yaml
EXAMPLES = r"""
- name: Update hypercore version
  scale_computing.hypercore.version_update:
    icos_version: 9.2.11.210763
  register: result
"""

# language=yaml
RETURN = r"""
record:
  description:
    - Version applied.
  returned: success
  type: dict
  contains:
    uuid:
      description: Unique identifier in format major_version.minor_version.revision.build_id.
      type: str
      sample: 9.2.11.210763
    description:
      description: |
        Human-readable name for the update.
        Empty if I(force_update=true).
      type: str
      sample: 9.2.11 General Availability
    change_log:
      description: |
        Description of all changes that are in this update, in HTML format.
        Empty if I(force_update=true).
      type: str
      sample: ...Please allow between 20-40 minutes per node for the update to complete...
    build_id:
      description: ID of the build which corresponds to this update
      type: int
      sample: 210763
    major_version:
      description: Major version number
      type: int
      sample: 9
    minor_version:
      description: Minor version number
      type: int
      sample: 2
    revision:
      description: Revision number
      type: int
      sample: 11
    timestamp:
      description: |
        Unix timestamp when the update was released.
        Value of 0 is returned if I(force_update=true).
      type: int
      sample: 0
"""

from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments
from ..module_utils import errors
from ..module_utils.client import Client
from ..module_utils.cluster import Cluster
from ..module_utils.hypercore_version import Update
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import TypedUpdateToAnsible


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[TypedUpdateToAnsible], Dict[Any, Any]]:
    cluster = Cluster.get(rest_client)
    new_icos_version = module.params["icos_version"]
    if cluster.icos_version == new_icos_version:
        return (
            False,
            None,
            dict(
                before=dict(icos_version=cluster.icos_version),
                after=dict(icos_version=cluster.icos_version),
            ),
        )
    update = None
    if module.params["force_update"]:
        if len(new_icos_version.split(".")) != 4:
            msg = f"HyperCore version must be in format 'major_version.minor_version.revision.build_id' - value {new_icos_version} is not valid."
            raise errors.InvalidModuleParam(msg)
        update = Update(
            uuid=new_icos_version,
            description="",
            change_log="",
            build_id=new_icos_version.split(".")[3],
            major_version=new_icos_version.split(".")[0],
            minor_version=new_icos_version.split(".")[1],
            revision=new_icos_version.split(".")[2],
            timestamp=0,
        )
    else:
        # check the requested version is listed under available versions
        update = Update.get(rest_client, new_icos_version, must_exist=True)
    if not isinstance(update, Update):
        raise AssertionError("update is not of type Update")  # mypy helper
    Update.apply_update(rest_client, new_icos_version)
    return (
        True,
        update.to_ansible(),
        dict(
            before=dict(icos_version=cluster.icos_version),
            after=dict(icos_version=new_icos_version),
        ),
    )


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            icos_version=dict(type="str", required=True),
            force_update=dict(type="bool", default=False),
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
