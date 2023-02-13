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

- name: Update previously create Email Alert Recipient
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
  type: list
  sample:
    - alert_tag_uuid: 0
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
    before = EmailAlert.get_state(rest_client)
    for item in before:
        if item.get("email_address") == module.params["email"]:
            return False, before, dict(before=before, after=before)
    EmailAlert.create(
        rest_client=rest_client,
        payload=dict(emailAddress=module.params["email"]),
        check_mode=module.check_mode,
    )
    after = EmailAlert.get_state(rest_client)
    return (
        after != before,
        after,
        dict(before=before, after=after),
    )  # changed, records, diff


def update_email_alert(module: AnsibleModule, rest_client: RestClient):
    before = EmailAlert.get_state(
        rest_client
    )  # get the records of emailAlert endpoint before update

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
    after = EmailAlert.get_state(
        rest_client
    )  # get the records od emailAlert endpoint after update
    return (
        after != before,
        after,
        dict(before=before, after=after),
    )  # changed, records, diff


def delete_email_alert(module: AnsibleModule, rest_client: RestClient):
    before = EmailAlert.get_state(rest_client)
    delete_email = EmailAlert.get_by_email(
        dict(email_address=module.params["email"]), rest_client
    )
    if not delete_email:
        module.warn("Email Alert: The email you're trying to remove, doesn't exist.")
        return False, before, dict(before=before, after=before)
    delete_email.delete(rest_client, module.check_mode)

    after = EmailAlert.get_state(rest_client)
    return (
        after != before,
        after,
        dict(before=before, after=after),
    )  # changed, records, diff


def send_test(module: AnsibleModule, rest_client: RestClient):
    before = EmailAlert.get_state(rest_client)

    if module.params["email_new"] is not None:
        module.warn("Email Alert: parameter 'email_new' is not needed.")

    send_email = EmailAlert.get_by_email(
        dict(email_address=module.params["email"]), rest_client
    )
    if not send_email:
        module.warn("Email Alert: can't send a test email to a nonexistent recipient.")

    send_email.test(
        rest_client=rest_client,
    )

    after = EmailAlert.get_state(rest_client)
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
        changed, records, diff = run(module, rest_client)
        module.exit_json(changed=changed, records=records, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
