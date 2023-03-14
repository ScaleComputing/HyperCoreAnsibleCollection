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
    certificate:|
      -----BEGIN CERTIFICATE-----
      MIIGKzCCBBOgAwIBAgIUWaGzXfgSUuwwPJu3F2Q/Ru/O8JQwDQYJKoZIhvcNAQEL
      ...
      -----END CERTIFICATE-----
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import (
    TypedDiff,
    TypedTaskTag,
    TypedCertificateToAnsible,
)
from ..module_utils.task_tag import TaskTag

from typing import Tuple, Optional
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
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[TypedCertificateToAnsible], TypedDiff]:
    before: TypedCertificateToAnsible = dict(certificate=get_certificate(module))
    task = upload_cert(module, rest_client)
    # After certificate is uploaded the cluster loses connection
    # Try 10 times to get task status
    max_retries = 10
    for ii in range(max_retries):
        try:
            TaskTag.wait_task(rest_client, task)
            break
        except ConnectionRefusedError:
            module.warn(
                f"retry {ii}/{max_retries}, ConnectionRefusedError - ignore and continue"
            )
            sleep(2)
            continue
        except ConnectionResetError:
            module.warn(
                f"retry {ii}/{max_retries}, ConnectionResetError - ignore and continue"
            )
            sleep(2)
            continue
        except errors.ScaleComputingError as ex:
            # Ignore "EOF occurred in violation of protocol (_ssl.c:997)"
            # Also other have same problem - https://github.com/psf/requests/issues/3006#issuecomment-183394849.
            # We do not use requests library, but problem is the same.
            # ex.args - this is what Exception.__init__() stores into object.
            ex_reason = ex.args[0]
            # ex_reason is instance of SSLEOFError or ssl.SSLEOFError
            strerror = ex_reason.strerror
            if (
                "EOF occurred in violation of protocol" in strerror
                and "ssl.c" in strerror
            ):
                module.warn(
                    f"retry {ii}/{max_retries}, SSLEOFError - ignore and continue"
                )
                sleep(2)
                continue
            else:
                module.warn(
                    f"retry {ii}/{max_retries}, re-raise unexpected exception" + str(ex)
                )
                raise
    after: TypedCertificateToAnsible = dict(certificate=get_certificate(module))
    return True, after, dict(before=before, after=after)


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Optional[TypedCertificateToAnsible], TypedDiff]:
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
