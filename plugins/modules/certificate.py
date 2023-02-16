#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: certificate

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Handles cluster SSL certificates.
description:
  - Can upload and verify SSL certificates.
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  certificate:
    description:
      - Plain text of the X.509 PEM-encode certificate.
    type: str
    required: true
  private_key:
    description:
      - Plain text of the RSA PEM-encoded private key.
    type: str
    required: true
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Upload new certificate
  scale_computing.hypercore.certificate:
    private_key: this_is_the_private_key
    certificate: this_is_the_certificate
"""

RETURN = r"""
record:
  description:
    - Certificate record.
  returned: success
  type: dict
  sample:
    private_key: this_is_the_private_key
    certificate: this_is_the_certificate
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.utils import is_changed
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import TypedDiff, TypedCertificateToAnsible

from typing import Union, Tuple
import requests, os


def verify_certificate():
    # raise errors.ScaleComputingError(os.getcwd())
    response = requests.get('https://google.com/', cert=('bla.pem', 'bla-key.pem'))
    raise errors.ScaleComputingError(response)


def ensure_present(
    module: AnsibleModule,
    rest_client: RestClient,
) -> Tuple[bool, Union[TypedCertificateToAnsible, None], TypedDiff, bool]:
    before = None
    after = None
    verify_certificate()
    return is_changed(before, after), after, dict(before=before, after=after)


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedCertificateToAnsible, None], TypedDiff, bool]:
    return ensure_present(module, rest_client)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            private_key=dict(
                type="str",
                required=True,
            ),
            certificate=dict(
                type="str",
                required=True,
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client=client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
