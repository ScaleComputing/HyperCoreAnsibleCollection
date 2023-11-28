#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type


# language=yaml
DOCUMENTATION = r"""
module: iso_info

author:
  - Tjaž Eržen (@tjazsch)
short_description: Retrieve ISO images
description:
  - Retrieve a list of ISO images from HyperCore API endpoint C(/rest/v1/ISO).
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.iso
options:
  name:
    type: str
    description:
      - ISO image's name.
      - If specified, the ISO image with that specific name will get returned.
      - Otherwise, all ISO images are going to get listed.
"""


# language=yaml
EXAMPLES = r"""
- name: Retrieve all ISO images
  scale_computing.hypercore.iso_info:
  register: result

- name: Retrieve a specific ISO image by name
  scale_computing.hypercore.iso_info:
    name: SW_DVD9_Win_Server_STD_CORE_2022_2108.11_64Bit_English_DC_STD_MLF_X23-17134.ISO
  register: result
"""


# language=yaml
RETURN = r"""
records:
  description:
    - ISO images for which we're performing the query.
    - If I(name) is specified, the module will return exactly one record, if the record exists, and 0, if there is no matching name.
    - If I(name) is not specified, all ISO images will be returned
  returned: success
  type: list
  elements: dict
  contains:
    mounts:
      description: VMs this image is attached to
      type: list
      elements: dict
      sample:
        vm_uuid: 51e6d073-7566-4273-9196-58720117bd7f
        vm_name: xlab
    name:
      description: Filename of the image
      type: str
      sample: SW_DVD9_Win_Server_STD_CORE_2022_2108.11_64Bit_English_DC_STD_MLF_X23-17134.ISO
    path:
      description: Storage device used in conjunction with VirDomainBlockDevice.path
      type: str
      sample: scribe/171afce9-2452-4294-9bc4-6e8ae49f7e4c
    ready_for_insert:
      description:
        - The flag indicates the ISO image content is fully uploaded, and image is ready to be used.
        - Flag is `false` only for images that are in middle of upload, or where upload was terminated in middle.
      type: bool
      sample: true
    size:
      description: Size of the ISO file, in bytes
      type: int
      sample: 5110759424
    uuid:
      description: Unique identifier
      type: str
      sample: 171afce9-2452-4294-9bc4-6e8ae49f7e4c
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.utils import get_query
from ..module_utils.iso import ISO


def run(module, rest_client):
    query = get_query(module.params, "name", ansible_hypercore_map=dict(name="name"))
    return [
        ISO.from_hypercore(hypercore_data=hypercore_dict).to_ansible()
        for hypercore_dict in rest_client.list_records("/rest/v1/ISO", query)
    ]


def main():
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
        rest_client = RestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
