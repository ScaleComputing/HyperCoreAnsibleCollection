#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: email_alert

author:
  - Ana Zobec (@anazobec)
short_description: Create, update, delete or send test emails to Email Alert Recipients on HyperCore API.
description:
  - Use this module to create, update, delete or send test emails to the
    Email Alert Recipients configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.email_alert_info
options:
  email:
    type: str
    description:
      - An Email address of a recipient you wish to create, update, delete or send test emails to.
    required: True
  email_new:
    type: str
    description:
      - An Email address with which the existing email on the HyperCore API will be updated.
  state:
    type: str
    choices: [ present, absent, test ]
    description:
      - The desired state of the email alert recipient on HyperCore API.
      - If I(state=present) and C(email_new) wasn't provided,
        a new Email Alert Recipient will be added on the HyperCore API.
      - If I(state=absent), the Email Alert Recipient with the provided
        C(email) will be removed from HyperCore API.
      - If I(state=test), a test email will be sent to the provided
        Email Alert Recipient on HyperCore API.
    required: True
notes:
 - C(check_mode) is not supported.
"""


EXAMPLES = r"""
- name: Create a new Email Alert Recipient
  scale_computing.hypercore.email_alert:
    email: example@example.com
    state: present

- name: Update previously created Email Alert Recipient
  scale_computing.hypercore.email_alert:
    email: example@example.com
    email_new: new@example.com
    state: present

- name: Remove previously updated Email Alert Recipient
  scale_computing.hypercore.email_alert:
    email: new@example.com
    state: absent

- name: Send a test email to an Email Alert Recipient
  scale_computing.hypercore.email_alert:
    email: recipient@example.com
    state: test
"""

RETURN = r"""
records:
  description:
    - Output from modifying entries of the Email Alert Recipients on HyperCore API.
  returned: success
  type: dict
  sample:
    alert_tag_uuid: 0
    email_address: sample@sample.com
    latest_task_tag:
      completed: 1675680830
      created: 1675680830
      descriptionParameters: []
      formattedDescription: Create Alert Email Target
      formattedMessage: ""
      messageParameters: []
      modified: 1675680830
      nodeUUIDs: []
      objectUUID: 8664ed18-c354-4bab-be96-78dae5f6377f
      progressPercent: 100
      sessionID: 2bed8c34-1ef3-4366-8895-360f4f786afe
      state: COMPLETE
      taskTag: 813
    resend_delay: 86400
    silent_period: 900
    uuid: 8664ed18-c354-4bab-be96-78dae5f6377f
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.email_alert import EmailAlert

# from ..module_utils.typed_classes import TypedEmailAlertToAnsible, TypedDiff

# from typing import List, Tuple, Union, Dict, Any


def create_email_alert(module: AnsibleModule, rest_client: RestClient):
    email_alert = EmailAlert.get_by_email(
        dict(email_address=module.params["email"]), rest_client
    )

    # If that email alert recipient already exists, it will not be created again (no duplicates)
    if email_alert:
        before = email_alert.to_ansible()
        return False, before, dict(before=before, after=before)

    # Otherwise, create that email alert recipient
    create_email = EmailAlert.create(
        rest_client=rest_client,
        payload=dict(emailAddress=module.params["email"]),
        check_mode=module.check_mode,
    )

    # after = create_email.to_ansible()
    after = create_email.to_ansible()
    return (
        True,
        after,
        dict(before={}, after=after),
    )  # changed, records, diff


def update_email_alert(module: AnsibleModule, rest_client: RestClient):
    # Get record of old emailAlert by email
    old_email = EmailAlert.get_by_email(
        dict(email_address=module.params["email"]), rest_client
    )

    if not old_email:
        old_email = EmailAlert.get_by_email(
            dict(email_address=module.params["email_new"]), rest_client
        )
        if not old_email:
            raise errors.ScaleComputingError(
                "Email Alert: Can't update a nonexistent email."
            )

    before = old_email.to_ansible()

    # Return if there are no changes
    if (
        module.params["email_new"] == old_email.to_ansible().get("email_address")
        or module.params["email_new"] == module.params["email"]
    ):
        return False, before, dict(before=before, after=before)

    # Otherwise, update with new email address
    old_email.update(
        rest_client=rest_client,
        payload=dict(emailAddress=module.params["email_new"]),
        check_mode=module.check_mode,
    )
    new_email = EmailAlert.get_by_email(
        dict(email_address=module.params["email_new"]), rest_client
    )
    after = new_email.to_ansible()

    return (
        True,
        after,
        dict(before=before, after=after),
    )  # changed, records, diff


def delete_email_alert(module: AnsibleModule, rest_client: RestClient):
    delete_email = EmailAlert.get_by_email(
        dict(email_address=module.params["email"]), rest_client
    )

    if not delete_email:
        return False, {}, dict(before={}, after={})

    before = delete_email.to_ansible()
    delete_email.delete(rest_client, module.check_mode)

    return (
        True,
        {},
        dict(before=before, after={}),
    )  # changed, records, diff


def send_test(module: AnsibleModule, rest_client: RestClient):
    send_email = EmailAlert.get_by_email(
        dict(email_address=module.params["email"]), rest_client
    )

    if (
        not send_email
    ):  # should the module notify user, that the email he's trying to test doesn't exist?
        module.warn("Email Alert: can't send a test email to a nonexistent recipient.")
        return False, {}, dict(before={}, after={})

    before = send_email.to_ansible()
    send_email.test(
        rest_client=rest_client,
    )

    after_send_email = EmailAlert.get_by_email(
        dict(email_address=module.params["email"]), rest_client
    )
    after = after_send_email.to_ansible()

    return after != before, after, dict(before=before, after=after)


def run(module: AnsibleModule, rest_client: RestClient):
    state = module.params["state"]
    if state == "present":
        if module.params["email_new"] is not None:
            return update_email_alert(module, rest_client)
        return create_email_alert(module, rest_client)
    elif state == "absent":
        return delete_email_alert(module, rest_client)

    # Else, state == "test"
    return send_test(module, rest_client)


def validate_params(module):
    if module.params["email_new"] is not None and module.params["state"] != "present":
        msg = "email_new can be used only if state==present"
        module.fail_json(msg=msg)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            email=dict(
                type="str",
                required=True,
            ),
            email_new=dict(
                type="str",
                required=False,
            ),
            state=dict(
                type="str",
                choices=["present", "absent", "test"],
                required=True,
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        validate_params(module)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
