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
      - File location containing the X.509 PEM-encode certificate.
    type: str
    required: true
  private_key:
    description:
      - File location containing the RSA PEM-encoded private key.
    type: str
    required: true
notes:
  - C(check_mode) is not supported.
"""

EXAMPLES = r"""
- name: Upload new certificate
  scale_computing.hypercore.certificate:
    private_key: "{{ lookup('file', 'private_key.pem') }}"
    certificate: "{{ lookup('file', 'scale_cert.cer') }}"
"""

RETURN = r"""
record:
  description:
    - Certificate record.
  returned: success
  type: dict
  sample:
    certificate: this_is_the_certificate
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.utils import is_changed
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import (
    TypedDiff,
    TypedTaskTag,
    TypedCertificateToAnsible,
)
from ..module_utils.task_tag import TaskTag

from typing import Union, Tuple
import ssl
from time import sleep


def get_certificate(module: AnsibleModule) -> str:
    host = (
        module.params["cluster_instance"]["host"]
        .replace("https://", "")
        .replace("http://", "")
    )
    cert = ssl.get_server_certificate((host, 443))
    return cert


def upload_cert(module: AnsibleModule, rest_client: RestClient) -> TypedTaskTag:
    payload = dict(
        certificate=module.params["certificate"],
        privateKey=module.params["private_key"],
    )
    response = rest_client.create_record("/rest/v1/Certificate", payload, False)
    return response


def ensure_present(
    module: AnsibleModule,
    rest_client: RestClient,
) -> Tuple[bool, Union[TypedCertificateToAnsible, None], TypedDiff]:
    before: TypedCertificateToAnsible = dict(certificate=get_certificate(module))
    # Don't upload if not necessary
    if before["certificate"].replace("\n", "") == module.params["certificate"].replace(
        "\n", ""
    ):
        return False, None, dict(before=None, after=None)
    else:
        task = upload_cert(module, rest_client)
        # After certificate is uploaded the cluster loses connection
        # Try 10 times to get task status
        max_retries = 10
        for ii in range(max_retries):
            try:
                TaskTag.wait_task(rest_client, task)
                break
            except (
                errors.ScaleComputingError
            ) as ex:  # ConnectionRefusedError not working
                if str(ex) == "[Errno 111] Connection refused":
                    sleep(2)
                    continue
                else:
                    raise errors.ScaleComputingError(ex)
        after: TypedCertificateToAnsible = dict(certificate=get_certificate(module))
    return is_changed(before, after), after, dict(before=before, after=after)


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedCertificateToAnsible, None], TypedDiff]:
    return ensure_present(module, rest_client)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            private_key=dict(
                type="str",
                required=True,
                no_log=True,
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
