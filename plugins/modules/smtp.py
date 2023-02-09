#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: smtp

author:
  - Ana Zobec (@anazobec)
short_description: Modify SMTP configuration on HyperCore API.
description:
  - Use this module to modify a SMTP configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.smtp_info
options:
  server:
    type: str
    description:
      - IP address or hostname of the SMTP server.
      - This parameter B(must always) be provided.
    required: True
  port:
    type: int
    description:
      - TCP port number of the SMTP server.
      - This parameter B(must always) be provided.
    required: True
  use_ssl:
    type: bool
    description:
      - Enable/disable SSL encryption.
      - Using SSL is recommended to avoid sending login information
        in clear text. Ensure the SMTP server supports SSL/TLS connections.
    required: False
    default: False
  use_auth:
    type: bool
    description:
      - Enable/disable authentication with C(auth_user) and C(auth_password).
    required: False
    default: False
  auth_user:
    type: str
    description:
      - Username for authentication if I(use_auth=True).
  auth_password:
    type: str
    description:
      - Password for authentication if I(use_auth=True).
  from_address:
    type: str
    description:
      - Email address the system alerts will be sent from.
    required: False
notes:
  - C(check_mode) is not supported.
  - SMTP authentication can be configured using username and password.
    In this case the configured username is returned, but password is not.
    Returned password is always empty string ("").
"""


EXAMPLES = r"""
- name: Modify SMTP configuration (authorization disabled)
  scale_computing.hypercore.smtp:
    server: smtp-relay.gmail.com
    port: 25
    use_ssl: false
    use_auth: false
    from_address: example@example.com

- name: Modify SMTP configuration (authorization enabled)
  scale_computing.hypercore.smtp:
    server: smtp-relay.gmail.com
    port: 25
    use_ssl: false
    use_auth: true
    auth_user: example
    auth_password: example123
    from_address: example@example.com
"""

RETURN = r"""
results:
  description:
    - Output from modifying entries of the SMTP configuration on HyperCore API.
  returned: success
  type: dict
  sample:
    auth_user: ""
    auth_password: ""
    from_address: PUB6@scalecomputing.com
    latest_task_tag:
      completed: 1675435601
      created: 1675435601
      descriptionParameters: []
      formattedDescription: Update Alert SMTP Config
      formattedMessage: ""
      messageParameters: []
      modified: 1675435601
      nodeUUIDs: []
      objectUUID: smtpconfig_guid
      progressPercent: 100
      sessionID: 92b4a736-259c-4f3c-9492-ce0c36691372
      state: COMPLETE
      taskTag: 761
    port: 25
    smtp_server: smtp-relay.gmail.com
    use_auth: false
    use_ssl: false
    uuid: smtpconfig_guid
"""


from ansible.module_utils.basic import AnsibleModule

from typing import Tuple, Union, Any, Dict
from ..module_utils.typed_classes import TypedSmtpToAnsible
from ..module_utils.task_tag import TaskTag
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.smtp import SMTP


def build_entry(
    api_entry: Any,
    module_entry: Any,
    module: AnsibleModule = None,  # use module param for debugging
) -> Tuple[Any, bool]:
    if module_entry is None:
        return api_entry, False

    change_needed = module_entry != api_entry

    if module:
        module.warn("module_entry: " + str(module_entry))
        module.warn("api_entry: " + str(api_entry))
        module.warn("change_needed: " + str(change_needed))

    return module_entry, change_needed


def modify_smtp_config(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[
    bool,
    Union[TypedSmtpToAnsible, Dict[Any, Any]],
    Dict[str, Union[TypedSmtpToAnsible, Dict[Any, Any]]],
]:
    # GET method to get the SMTP config by UUID
    smtp = SMTP.get_by_uuid(module.params, rest_client)

    if module.params["auth_password"] is None:
        new_auth_password = ""
    else:
        new_auth_password = module.params["auth_password"]
    if module.params["auth_user"] is None:
        new_auth_user = ""
    else:
        new_auth_user = module.params["auth_user"]

    payload = dict(
        smtpServer=module.params["server"],
        port=module.params["port"],
        useSSL=module.params["use_ssl"],
        useAuth=module.params["use_auth"],
        authUser=new_auth_user,
        authPassword=new_auth_password,
        fromAddress=module.params["from_address"],
    )

    # If SMTP config doesn't exist, create the
    # SMTP config with given parameters
    if not smtp:
        module.warn("SMTP: There is no SMTP configuration.")
        create_task_tag = rest_client.create_record(
            endpoint="/rest/v1/AlertSMTPConfig",
            payload=payload,
            check_mode=module.check_mode,
        )
        TaskTag.wait_task(rest_client, create_task_tag)
        # created_smtp = SMTP.get_by_uuid(module.params, rest_client)
        record = SMTP.get_state(rest_client)
        return True, record, dict(before={}, after=record)

    # Otherwise, continue with modifying the configuration
    before = smtp.to_ansible()
    old_state = smtp.get_state(
        rest_client
    )  # get the state of SMTP config before modification

    new_smtp_server, new_smtp_server_change_needed = build_entry(
        before.get("smtp_server"), module.params["server"]
    )
    new_port, new_port_change_needed = build_entry(
        before.get("port"), module.params["port"]
    )
    new_use_ssl, new_use_ssl_change_needed = build_entry(
        before.get("use_ssl"), module.params["use_ssl"]
    )
    new_use_auth, new_use_auth_change_needed = build_entry(
        before.get("use_auth"), module.params["use_auth"]
    )
    new_auth_user, new_auth_user_change_needed = build_entry(
        before.get("auth_user"), module.params["auth_user"]
    )
    new_auth_password, new_auth_password_change_needed = build_entry(
        before.get("auth_password"), module.params["auth_password"]
    )
    new_from_address, new_from_address_change_needed = build_entry(
        before.get("from_address"), module.params["from_address"]
    )

    # Init return values and return if no changes were made
    change, record, diff = (
        new_smtp_server_change_needed
        or new_port_change_needed
        or new_use_ssl_change_needed
        or new_use_auth_change_needed
        or new_auth_user_change_needed
        or new_auth_password_change_needed
        or new_from_address_change_needed,
        old_state,
        dict(before=old_state, after=old_state),
    )
    if not change:
        return change, record, diff

    # Set payload
    payload = dict(
        smtpServer=new_smtp_server,
        port=new_port,
        useSSL=new_use_ssl,
        useAuth=new_use_auth,
        authUser=new_auth_user,
        authPassword=new_auth_password,
        fromAddress=new_from_address,
    )

    # Set the task tag
    # update_record -> PATCH
    update_task_tag = rest_client.update_record(
        endpoint="{0}/{1}".format("/rest/v1/AlertSMTPConfig", smtp.uuid),
        payload=payload,
        check_mode=module.check_mode,
    )

    TaskTag.wait_task(rest_client, update_task_tag)  # wait for task to finish

    record = SMTP.get_state(rest_client)
    diff = dict(before=old_state, after=record)
    change = old_state != record

    return change, record, diff


def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[
    bool,
    Union[TypedSmtpToAnsible, Dict[Any, Any]],
    Dict[str, Union[TypedSmtpToAnsible, Dict[Any, Any]]],
]:
    return modify_smtp_config(module, rest_client)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            server=dict(
                type="str",
                required=True,
            ),
            port=dict(
                type="int",
                required=True,
            ),
            use_ssl=dict(
                type="bool",
                default=False,
                required=False,
            ),
            use_auth=dict(
                type="bool",
                default=False,
                required=False,
            ),
            auth_user=dict(
                type="str",
                required=False,
            ),
            auth_password=dict(
                type="str",
                no_log=True,
                required=False,
            ),
            from_address=dict(
                type="str",
                default="",
                required=False,
            ),
        ),
        required_if=[
            (
                "use_auth",
                True,
                (
                    "auth_user",
                    "auth_password",
                ),
            )
        ],
    )

    try:
        client = Client(
            host=module.params["cluster_instance"]["host"],
            username=module.params["cluster_instance"]["username"],
            password=module.params["cluster_instance"]["password"],
        )
        rest_client = RestClient(client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
