#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: registration_info

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Retrieve information about cluster registration.
description:
  - Retrieve information about cluster registration.
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
"""

EXAMPLES = r"""
- name: Get registration info
  scale_computing.hypercore.registration_info:
  register: output
  
- name: output the registration info
  debug:
    var: output
"""

RETURN = r"""
records:
  description:
    - A list of cluster registration info
  returned: success
  type: list
  sample:
    - cluster_data_hash: data_hash
      cluster_data_hash_accepted: data_hash_accepted
      cluster_id: this_cluster_id
      company_name: sample_company
      contact: John Smith
      email: john_smith@sgmail.com
      phone: '777777777'
      uuid: registration_guid
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.registration import Registration
from ..module_utils.rest_client import CachedRestClient


def run(module, rest_client):
    return [ Registration.from_hypercore(registration_dict).to_ansible() for registration_dict in rest_client.list_records("/rest/v1/Registration") ]


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = CachedRestClient(client)
        records = run(module, rest_client)
        module.exit_json(changed=False, records=records)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
