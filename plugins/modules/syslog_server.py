#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


# language=yaml
DOCUMENTATION = r"""
module: syslog_server

author:
  - Ana Zobec (@anazobec)
short_description: Create, update or delete Syslog servers from HyperCore API.
description:
  - Use this module to create, update or delete Syslog servers from
    the Syslog Servers configuration on HyperCore API.
  - A single syslog server can be created/updated/removed using I(state=present/absent)
    and C(host), C(port), C(protocol).
    In this case, return value C(record) is set, but return value C(records) is empty list.
  - All syslog servers can be reconfigured at once using I(state=set) and C(syslog_servers).
    C(syslog_servers) is a list with C(host), C(port), C(protocol) attributes.
    In this case, return value C(record) is empty dict, and return value C(records) lists configured servers.
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
  host_new:
    type: str
    description:
      - An IP address or hostname with which the existing Syslog server
        host on the HyperCore API will be updated.
  port: &port
    type: int
    default: 514
    description:
      - Network port of the syslog server.
  protocol: &protocol
    type: str
    default: udp
    choices: [ udp, tcp ]
    description:
      -  Network protocol used to send syslog alerts.
  syslog_servers:
    type: list
    elements: dict
    default: []
    suboptions:
      host:
        type: str
        description:
          - An IP address or hostname of the Syslog server you wish to create, update or delete.
        required: True
      port: *port
      protocol: *protocol
    description:
      - List of syslog servers to set.
  state:
    type: str
    choices: [ present, absent, set ]
    description:
      - The desired state of the syslog server on HyperCore API.
      - If I(state=present) a new Syslog server will be added,
        or existing Syslog server with matching C(host) will be updated.
      - C(host) of existing Syslog server can be changed by specifying both C(host) and C(host_new).
      - If I(state=absent), the Syslog server with the provided
        C(host) will be removed from HyperCore API.
      - If I(state=set), then C(syslog_servers) will be used to configure HyperCore API.
    required: True
notes:
 - C(check_mode) is not supported.
"""


# language=yaml
EXAMPLES = r"""
- name: Set all Syslog servers - this removes everything not listed in syslog_servers
  scale_computing.hypercore.syslog_server:
    syslog_servers:
      - host: 10.5.11.222
        port: 514
        protocol: udp
      - host: 10.5.11.223
        port: 10514
        protocol: tcp
    state: set

- name: Create a single Syslog server - leaves other Syslog servers unmodifed
  scale_computing.hypercore.syslog_server:
    host: 10.5.11.222
    port: 514
    protocol: udp
    state: present

- name: Update a single existing Syslog server - leaves other Syslog servers unmodifed
  scale_computing.hypercore.syslog_server:
    host: 10.5.11.222
    host_new: 1.2.3.4
    port: 514
    protocol: udp
    state: present

- name: Delete a single Syslog server - leaves other Syslog servers unmodifed
  scale_computing.hypercore.syslog_server:
    host: 10.5.11.222
    state: absent
"""

# language=yaml
RETURN = r"""
record:
  description:
    - Created or updated syslog server.
  returned: success
  type: dict
  contains:
    alert_tag_uuid:
      description: Unique identifier for an AlertTag (internal)
      type: str
      sample: 0
    host:
      description: IP address or hostname of the syslog server
      type: str
      sample: 10.5.11.222
    latest_task_tag:
      description: Latest Task Tag
      type: dict
      sample:
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
    port:
      description: Network port of the syslog server
      type: int
      sample: 514
    protocol:
      description: Network protocol used to send syslog alerts
      type: str
      sample: udp
    resend_delay:
      description: Alert resend delay in seconds
      type: int
      sample: 86400
    silent_period:
      description: Alerts will not resend if there are additional event triggers within this time in seconds
      type: str
      sample: 900
    uuid:
      description: Unique identifer
      type: str
      sample: 21c65667-234a-437b-aead-df0199598ff9
records:
  description: List of syslog servers
  returned: success
  type: list
  elements: dict
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.syslog_server import SyslogServer
from ..module_utils.typed_classes import TypedSyslogServerToAnsible, TypedDiff
from typing import Tuple, Union, Dict, Any, List, Optional


UDP = "SYSLOG_PROTOCOL_UDP"  # default
TCP = "SYSLOG_PROTOCOL_TCP"
DEFAULT_PORT = 514


def get_protocol(protocol: str) -> str:
    return UDP if protocol == "udp" else TCP


def create_syslog_server(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[
    bool, TypedSyslogServerToAnsible, List[TypedSyslogServerToAnsible], TypedDiff
]:
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
        SyslogServer.get_state(rest_client),
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
            payload["protocol"] = module.params["protocol"]
    return payload


def update_syslog_server(
    old_syserver: SyslogServer, module: AnsibleModule, rest_client: RestClient
) -> Tuple[
    bool,
    Union[TypedSyslogServerToAnsible, Dict[None, None]],
    List[TypedSyslogServerToAnsible],
    TypedDiff,
]:
    old_syserver_tmp = old_syserver
    if not old_syserver:
        if module.params["host_new"]:
            old_syserver_tmp = SyslogServer.get_by_host(
                module.params["host_new"], rest_client
            )  # type: ignore
    if not old_syserver_tmp:
        # Syslog server not found by old or by new host, do nothing.
        # Maybe module should fail with error instead.
        records_after = SyslogServer.get_state(rest_client)
        return False, {}, records_after, dict(before={}, after={})

    before = old_syserver_tmp.to_ansible()
    payload = build_update_payload(module, old_syserver_tmp)
    before_payload = old_syserver_tmp.to_hypercore()

    # Return if there are no changes
    if not before or payload == before_payload:
        records_after = SyslogServer.get_state(rest_client)
        return False, before, records_after, dict(before=before, after=before)

    # Otherwise, update with new parameters
    payload["protocol"] = get_protocol(payload["protocol"])

    old_syserver_tmp.update(
        rest_client=rest_client,
        payload=payload,
        check_mode=module.check_mode,
    )

    new_syserver = SyslogServer.get_by_host(
        host=payload["host"], rest_client=rest_client
    )
    after = new_syserver.to_ansible()  # type: ignore

    records_after = SyslogServer.get_state(rest_client)
    return (
        after != before,
        after,
        records_after,
        dict(before=before, after=after),
    )  # changed, record, records, diff


def delete_syslog_server(
    delete_syserver: Optional[SyslogServer],
    module: AnsibleModule,
    rest_client: RestClient,
) -> Tuple[
    bool,
    Union[TypedSyslogServerToAnsible, Dict[None, None]],
    List[TypedSyslogServerToAnsible],
    TypedDiff,
]:
    if not delete_syserver:
        records_after = SyslogServer.get_state(rest_client)
        return False, {}, records_after, dict(before={}, after={})

    before = delete_syserver.to_ansible()
    delete_syserver.delete(rest_client, module.check_mode)

    records_after = SyslogServer.get_state(rest_client)
    return (
        True,
        {},
        records_after,
        dict(before=before, after={}),
    )  # changed, records, diff


def set_syslog_servers(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[
    bool,
    Union[TypedSyslogServerToAnsible, Dict[None, None]],
    List[TypedSyslogServerToAnsible],
    TypedDiff,
]:
    """
    Just ensure first N servers match what is requested by syslog_servers module param.
    """
    old_hc3_syslog_servers = SyslogServer.get_all(rest_client)
    ansible_syslog_servers = [
        SyslogServer.from_ansible(ss) for ss in module.params["syslog_servers"]
    ]
    ansible_syslog_servers.sort()
    changed = False
    for ii, ansible_syslog_server in enumerate(ansible_syslog_servers):
        if ansible_syslog_server.protocol is None:
            raise AssertionError()
        payload = dict(
            host=ansible_syslog_server.host,
            port=ansible_syslog_server.port,
            protocol=get_protocol(ansible_syslog_server.protocol),
        )
        if ii < len(old_hc3_syslog_servers):
            # update existing HC3 syslog server
            hc3_syslog_server = old_hc3_syslog_servers[ii]
            if hc3_syslog_server.is_equivalent(ansible_syslog_server):
                continue
            hc3_syslog_server.update(rest_client, payload)
            changed = True
        else:
            # need to create new HC3 syslog server
            SyslogServer.create(rest_client, payload)
            changed = True
    # remove extra old_hc3_syslog_servers
    for ii in range(len(ansible_syslog_servers), len(old_hc3_syslog_servers)):
        hc3_syslog_server = old_hc3_syslog_servers[ii]
        hc3_syslog_server.delete(rest_client)
        changed = True

    # compute change
    records_before = [ss.to_ansible() for ss in old_hc3_syslog_servers]
    records_after = SyslogServer.get_state(rest_client)
    record_after: Dict[None, None] = {}

    return (
        changed,
        record_after,
        records_after,
        dict(before=records_before, after=records_after),
    )


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[
    bool,
    Union[TypedSyslogServerToAnsible, Dict[None, None]],
    List[TypedSyslogServerToAnsible],
    TypedDiff,
]:
    state = module.params["state"]
    if state == "set":
        return set_syslog_servers(module, rest_client)

    syslog_server = SyslogServer.get_by_host(
        host=module.params["host"], rest_client=rest_client
    )
    if state == "present":
        if syslog_server or module.params["host_new"] is not None:
            return update_syslog_server(syslog_server, module, rest_client)  # type: ignore
        return create_syslog_server(module, rest_client)

    # Else if state == "absent":
    return delete_syslog_server(syslog_server, module, rest_client)


def main() -> None:
    port_spec = dict(
        type="int",
        default=514,
        required=False,
    )
    protocol_spec = dict(
        type="str",
        choices=["udp", "tcp"],
        default="udp",
        required=False,
    )
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            host=dict(
                type="str",
                required=False,
            ),
            host_new=dict(
                type="str",
                required=False,
            ),
            port=port_spec,
            protocol=protocol_spec,
            syslog_servers=dict(
                type="list",
                elements="dict",
                default=[],
                options=dict(
                    host=dict(
                        type="str",
                        required=True,
                    ),
                    port=port_spec,
                    protocol=protocol_spec,
                ),
            ),
            state=dict(
                type="str",
                choices=["present", "absent", "set"],
                required=True,
            ),
        ),
        required_if=[
            ("state", "present", ("host",)),
            ("state", "absent", ("host",)),
            ("state", "set", ("syslog_servers",)),
        ],
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record, records, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, records=records, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
