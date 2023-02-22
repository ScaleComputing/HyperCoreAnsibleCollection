#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: syslog_server

author:
  - Ana Zobec (@anazobec)
short_description: Create, update or delete Syslog servers from HyperCore API.
description:
  - Use this module to create, update or delete Syslog servers from
    the Syslog Servers configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.syslog_server_info
options:
  host:
    type: str
    description:
      - An IP address or hostname of the Syslog server you wish to create, update or delete.
    required: True
  host_new:
    type: str
    description:
      - An IP address or hostname with which the existing Syslog server
        host on the HyperCore API will be updated.
  port:
    type: int
    default: 514
    description:
      - Network port of the syslog server.
  protocol:
    type: str
    default: udp
    choices: [ udp, tcp ]
    description:
      -  Network protocol used to send syslog alerts.
  state:
    type: str
    choices: [ present, absent ]
    description:
      - The desired state of the syslog server on HyperCore API.
      - If I(state=present) a new Syslog server will be added,
        or existing Syslog server with matching C(host) will be updated.
      - C(host) of existing Syslog server can be changed by specifying both C(host) and C(host_new).
      - If I(state=absent), the Syslog server with the provided
        C(host) will be removed from HyperCore API.
    required: True
notes:
 - C(check_mode) is not supported.
"""


EXAMPLES = r"""
- name: Create Syslog server
  scale_computing.hypercore.syslog_server:
    host: 10.5.11.222
    port: 514
    protocol: udp
    state: present

- name: Update existing Syslog server
  scale_computing.hypercore.syslog_server:
    host: 10.5.11.222
    host_new: 1.2.3.4
    port: 514
    protocol: udp
    state: present

- name: Delete Syslog server
  scale_computing.hypercore.syslog_server:
    host: 10.5.11.222
    state: absent
"""

RETURN = r"""
records:
  description:
    - Output from modifying entries of the Syslog Servers configuration on HyperCore API.
  returned: success
  type: dict
  sample:
    alert_tag_uuid: 0
    host: 10.5.11.222
    latest_task_tag:
      completed: 1623069193
      created: 1623069187
      descriptionParameters: []
      formattedDescription: Create Alert Syslog Target
      formattedMessage: ""
      messageParameters: []
      modified: 1623069193
      nodeUUIDs:
        - 32c5012d-7d7b-49b4-9201-70e02b0d8758
      objectUUID: 21c65667-234a-437b-aead-df0199598ff9
      progressPercent: 100
      sessionID: ""
      state: COMPLETE
      taskTag: 13
    port: 514
    protocol: SYSLOG_PROTOCOL_UDP
    resend_delay: 86400
    silent_period: 900
    uuid: 21c65667-234a-437b-aead-df0199598ff9
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.syslog_server import SyslogServer
from ..module_utils.typed_classes import TypedSyslogServerToAnsible, TypedDiff
from typing import Tuple, Union, Dict, Any


UDP = "SYSLOG_PROTOCOL_UDP"  # default
TCP = "SYSLOG_PROTOCOL_TCP"
DEFAULT_PORT = 514


def get_protocol(protocol: str) -> str:
    return UDP if protocol == "udp" else TCP


def create_syslog_server(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, TypedSyslogServerToAnsible, TypedDiff]:
    protocol = get_protocol(module.params["protocol"])

    # If that syslog server already exists, it will not be created again (no duplicates)

    # Otherwise, create that syslog server
    create_syserver = SyslogServer.create(
        rest_client=rest_client,
        payload=dict(
            host=module.params["host"],
            port=module.params["port"],
            protocol=protocol,
        ),
        check_mode=module.check_mode,
    )
    after = create_syserver.to_ansible()
    return (
        True,
        after,
        dict(before={}, after=after),
    )  # changed, records, diff


def build_update_payload(
    module: AnsibleModule, syslog_server: SyslogServer
) -> Dict[Any, Any]:
    payload = dict(
        host=syslog_server.host,
        port=syslog_server.port,
        protocol=syslog_server.protocol,
    )
    if module.params["host_new"] and syslog_server.host != module.params["host_new"]:
        payload["host"] = module.params["host_new"]
    if (
        module.params["port"] != DEFAULT_PORT
        and module.params["port"] != syslog_server.port
    ):
        payload["port"] = module.params["port"]
    if module.params["protocol"]:
        protocol = get_protocol(module.params["protocol"])
        if protocol != UDP and protocol != syslog_server.protocol:
            payload["protocol"] = protocol
    return payload


def update_syslog_server(
    old_syserver: SyslogServer, module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedSyslogServerToAnsible, Dict[None, None]], TypedDiff]:
    old_syserver_tmp = old_syserver
    if not old_syserver:
        if module.params["host_new"]:
            old_syserver_tmp = SyslogServer.get_by_host(
                module.params["host_new"], rest_client
            )  # type: ignore
    if not old_syserver_tmp:
        return False, {}, dict(before={}, after={})

    before = old_syserver_tmp.to_ansible()
    payload = build_update_payload(module, old_syserver_tmp)
    before_payload = old_syserver_tmp.to_hypercore()

    # Return if there are no changes
    if not before or payload == before_payload:
        return False, before, dict(before=before, after=before)

    # Otherwise, update with new parameters
    old_syserver.update(
        rest_client=rest_client,
        payload=payload,
        check_mode=module.check_mode,
    )

    new_syserver = SyslogServer.get_by_host(
        host=payload["host"], rest_client=rest_client
    )
    after = new_syserver.to_ansible()  # type: ignore

    return (
        after != before,
        after,
        dict(before=before, after=after),
    )  # changed, records, diff


def delete_syslog_server(
    delete_syserver: SyslogServer, module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedSyslogServerToAnsible, Dict[None, None]], TypedDiff]:
    if not delete_syserver:
        return False, {}, dict(before={}, after={})

    before = delete_syserver.to_ansible()
    delete_syserver.delete(rest_client, module.check_mode)

    return (
        True,
        {},
        dict(before=before, after={}),
    )  # changed, records, diff


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedSyslogServerToAnsible, Dict[None, None]], TypedDiff]:
    syslog_server = SyslogServer.get_by_host(
        host=module.params["host"], rest_client=rest_client
    )
    state = module.params["state"]
    if state == "present":
        if syslog_server or module.params["host_new"] is not None:
            return update_syslog_server(syslog_server, module, rest_client)  # type: ignore
        return create_syslog_server(module, rest_client)

    # Else if state == "absent":
    return delete_syslog_server(syslog_server, module, rest_client)  # type: ignore


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            host=dict(
                type="str",
                required=True,
            ),
            host_new=dict(
                type="str",
                required=False,
            ),
            port=dict(
                type="int",
                default=514,
                required=False,
            ),
            protocol=dict(
                type="str",
                choices=["udp", "tcp"],
                default="udp",
                required=False,
            ),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
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
