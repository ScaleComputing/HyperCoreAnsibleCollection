# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


# language=yaml
DOCUMENTATION = r"""
module: virtual_disk_info

author:
  - Justin Cinkelj (@justinc1)
short_description: List virtual disks on HyperCore API
description:
  - Use this module to list virtual disk on a HyperCore server.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
#  - module: scale_computing.hypercore.virtual_disk
options:
  name:
    type: str
    description:
      - Virtual disk name.
      - If specified, the virtual disk with that specific name will get returned.
      - Otherwise, all virtual disks are going to get listed.
"""


# language=yaml
EXAMPLES = r"""
- name: List all virtual disks
  scale_computing.hypercore.virtual_disk_info:

- name: List a single virtual disk
  scale_computing.hypercore.virtual_disk_info:
    name: demo-virtual-disk
"""

# language=yaml
RETURN = r"""
records:
  description:
    - A list of virtual_disk records.
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description: Name identifier
      type: str
      sample: demo-virtual-disk
    block_size:
      description: Size of individual blocks (the smallest unit of measurement for VSDs) on the drive, in bytes
      type: int
      sample: 1048576
    size:
      description: Total capacity, in bytes
      type: int
      sample: 1073741824
    replication_factor:
      description: How many copies of each block are stored on physical drives
      type: int
      sample: 2
    uuid:
      description: Unique identifier
      type: str
      sample: 7983b298-c37a-4c99-8dfe-b2952e81b092
"""


from ansible.module_utils.basic import AnsibleModule
from typing import List

from ..module_utils.typed_classes import (
    TypedVirtualDiskToAnsible,
)
from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient, CachedRestClient
from ..module_utils.utils import get_query
from ..module_utils.virtual_disk import VirtualDisk

from ..module_utils.hypercore_version import (
    HyperCoreVersion,
)

HYPERCORE_VERSION_REQUIREMENTS = ">=9.2.10"


def run(
    module: AnsibleModule, rest_client: RestClient
) -> List[TypedVirtualDiskToAnsible]:
    query = get_query(module.params, "name", ansible_hypercore_map=dict(name="name"))
    return VirtualDisk.get_state(rest_client, query)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(
                type="str",
                required=False,
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = CachedRestClient(client)
        hcversion = HyperCoreVersion(rest_client)
        hcversion.check_version(module, HYPERCORE_VERSION_REQUIREMENTS)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
