# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import unittest.mock as mock
import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert import (
    EmailAlert,
)
from ansible_collections.scale_computing.hypercore.plugins.modules import email_alert

from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestModifyEmailAlert:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )
        self.magic = mock.MagicMock()

    @pytest.mark.parametrize(
        ("rc_email_alert",),
        [
            (None,),
            (
                EmailAlert(
                    uuid="test",
                    alert_tag_uuid="0",
                    email_address="test@test.com",
                    resend_delay=123,
                    silent_period=123,
                    latest_task_tag={},
                ),
            ),
        ],
    )
    def test_create_email_alert(
        self, create_module, rest_client, task_wait, mocker, rc_email_alert
    ):
        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                email="test@test.com",
                state="present",
            )
        )
        task_tag = {
            "taskTag": 123,
            "createdUUID": "test",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert.EmailAlert.get_by_uuid"
        ).return_value = EmailAlert(uuid=task_tag["createdUUID"])

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert.EmailAlert.get_by_email"
        ).return_value = rc_email_alert
        rest_client.create_record.return_value = task_tag

        called_with_dict = dict(
            rest_client=rest_client,
            payload=dict(emailAddress="test@test.com"),
            check_mode=False,
        )
        EmailAlert.create = mock.create_autospec(EmailAlert.create)
        email_alert.create_email_alert(module, rest_client)
        if not rc_email_alert:
            EmailAlert.create.assert_called_once_with(**called_with_dict)
        else:
            EmailAlert.create.assert_not_called()

    @pytest.mark.parametrize(
        ("rc_email", "email", "email_new"),
        [
            ("email", "test@test.com", "new@test.com"),
            (None, "test@test.com", "new@test.com"),
            ("email", "test@test.com", "test@test.com"),
        ],
    )
    def test_update_email_alert(
        self, create_module, rest_client, task_wait, mocker, rc_email, email, email_new
    ):
        update_email = ""
        if rc_email == "email":
            email_on_client = email
            update_email = email_new
        elif rc_email == "email_new":
            email_on_client = email_new
            update_email = email
        else:
            email_on_client = None

        print("update_email: " + str(update_email))
        print("email_on_client: " + str(email_on_client))

        if email_on_client:
            rc_email_alert = EmailAlert(
                uuid="test",
                alert_tag_uuid="0",
                email_address=email_on_client,
                resend_delay=123,
                silent_period=123,
                latest_task_tag={},
            )
        else:
            rc_email_alert = None

        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                email=email,
                email_new=email_new,
                state="present",
            )
        )
        task_tag = {
            "taskTag": 123,
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert.EmailAlert.get_by_email"
        ).return_value = rc_email_alert
        rest_client.update_record.return_value = task_tag

        called_with_dict = dict(
            rest_client=rest_client,
            payload=dict(emailAddress=update_email),
            check_mode=False,
        )
        print(rc_email_alert)

        EmailAlert.update = mock.create_autospec(EmailAlert.update)

        if rc_email_alert:
            email_alert.update_email_alert(module, rest_client)
            if update_email == email_on_client or email == email_new:
                EmailAlert.update.assert_not_called()
            else:
                EmailAlert.update.assert_called_once_with(
                    rc_email_alert, **called_with_dict
                )
        else:
            with pytest.raises(errors.ScaleComputingError):
                email_alert.update_email_alert(module, rest_client)

    @pytest.mark.parametrize(
        ("rc_email_alert", "email"),
        [
            (None, "test@test.com"),
            (
                EmailAlert(
                    uuid="test",
                    alert_tag_uuid="0",
                    email_address="test@test.com",
                    resend_delay=123,
                    silent_period=123,
                    latest_task_tag={},
                ),
                "test@test.com",
            ),
        ],
    )
    def test_delete_email_alert(
        self, create_module, rest_client, task_wait, mocker, rc_email_alert, email
    ):
        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                email=email,
                state="absent",
            )
        )
        task_tag = {
            "taskTag": 123,
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert.EmailAlert.get_by_email"
        ).return_value = rc_email_alert
        rest_client.update_record.return_value = task_tag

        called_with_dict = dict(
            rest_client=rest_client,
            check_mode=False,
        )

        EmailAlert.delete = mock.create_autospec(EmailAlert.delete)
        email_alert.delete_email_alert(module, rest_client)
        if rc_email_alert:
            EmailAlert.delete.assert_called_once_with(
                rc_email_alert, **called_with_dict
            )
        else:
            EmailAlert.delete.assert_not_called()

    @pytest.mark.parametrize(
        ("rc_email_alert", "email"),
        [
            (None, "test@test.com"),
            (
                EmailAlert(
                    uuid="test",
                    alert_tag_uuid="0",
                    email_address="test@test.com",
                    resend_delay=123,
                    silent_period=123,
                    latest_task_tag={},
                ),
                "test@test.com",
            ),
        ],
    )
    def test_send_test(
        self, create_module, rest_client, task_wait, mocker, rc_email_alert, email
    ):
        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                email=email,
                state="test",
            )
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert.EmailAlert.get_by_email"
        ).return_value = rc_email_alert
        rest_client.client.post.return_value = None

        called_with_dict = dict(
            rest_client=rest_client,
        )

        EmailAlert.test = mock.create_autospec(EmailAlert.test)
        email_alert.send_test(module, rest_client)
        if rc_email_alert:
            EmailAlert.test.assert_called_once_with(rc_email_alert, **called_with_dict)
        else:
            EmailAlert.test.assert_not_called()


class TestMain:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )

    def test_fail(self, run_main):
        success, result = run_main(email_alert)

        print(result["msg"])

        assert success is False
        assert (
            "missing required arguments: state, email" in result["msg"]
            or "missing required arguments: email, state" in result["msg"]
        )

    @pytest.mark.parametrize(
        ("email", "email_new", "state"),
        [
            ("test@test.com", None, "present"),
            ("test@test.com", "new@test.com", "present"),
            ("test@test.com", None, "absent"),
            ("test@test.com", None, "test"),
        ],
    )
    def test_params(
        self,
        run_main,
        email,
        email_new,
        state,
    ):
        params = dict(
            cluster_instance=self.cluster_instance,
            email=email,
            email_new=email_new,
            state=state,
        )
        success, result = run_main(email_alert, params)

        assert success is True
