# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert import (
    EmailAlert,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestEmailAlert:
    def setup_method(self):
        self.email_alert = EmailAlert(
            uuid="8664ed18-c354-4bab-be96-78dae5f6377f",
            alert_tag_uuid="0",
            email_address="test@test.com",
            resend_delay=123,
            silent_period=123,
            latest_task_tag={},
        )
        self.from_hypercore_dict = dict(
            uuid="8664ed18-c354-4bab-be96-78dae5f6377f",
            alertTagUUID="0",
            emailAddress="test@test.com",
            resendDelay=123,
            silentPeriod=123,
            latestTaskTag={},
        )
        self.to_hypercore_dict = dict(
            alertTagUUID="0",
            emailAddress="test@test.com",
            resendDelay=123,
            silentPeriod=123,
        )
        self.ansible_dict = dict(
            uuid="8664ed18-c354-4bab-be96-78dae5f6377f",
            alert_tag_uuid="0",
            email_address="test@test.com",
            resend_delay=123,
            silent_period=123,
            latest_task_tag={},
        )

    def test_email_alert_to_hypercore(self):
        assert self.email_alert.to_hypercore() == self.to_hypercore_dict

    def test_email_alert_from_hypercore_dict_not_empty(self):
        email_alert_from_hypercore = EmailAlert.from_hypercore(self.from_hypercore_dict)
        assert self.email_alert == email_alert_from_hypercore

    def test_email_alert_from_hypercore_dict_empty(self):
        assert EmailAlert.from_hypercore([]) is None

    def test_email_alert_to_ansible(self):
        assert self.email_alert.to_ansible() == self.ansible_dict

    def test_email_alert_from_ansible(self):
        email_alert_from_ansible = EmailAlert.from_ansible(self.ansible_dict)
        assert self.email_alert == email_alert_from_ansible

    def test_get_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(**self.from_hypercore_dict)
        ansible_dict = dict(
            uuid="test",
        )
        email_alert_from_hypercore = EmailAlert.get_by_uuid(ansible_dict, rest_client)
        assert email_alert_from_hypercore == self.email_alert

    def test_get_state(self, rest_client):
        rest_client.list_records.return_value = [
            self.from_hypercore_dict,
            self.from_hypercore_dict,
        ]

        expected = {
            "uuid": "8664ed18-c354-4bab-be96-78dae5f6377f",
            "alert_tag_uuid": "0",
            "email_address": "test@test.com",
            "resend_delay": 123,
            "silent_period": 123,
            "latest_task_tag": {},
        }
        result = EmailAlert.get_state(rest_client)
        print(result)

        assert result == [expected, expected]

    def test_get_state_no_record(self, rest_client):
        rest_client.list_records.return_value = []

        result = EmailAlert.get_state(rest_client)
        assert result == []

    # def test_get_by_email(self, rest_client):
    #     other_hypercore_dict = self.from_hypercore_dict
    #     other_hypercore_dict["email_address"] = "test1@test.com"
    #     rest_client.get_record.return_value = [
    #         self.from_hypercore_dict,
    #     ]
    #
    #     result = EmailAlert.get_by_email(dict(email_address="test@test.com"), rest_client)
    #     print(result)
    #     assert result == {
    #         "uuid": "8664ed18-c354-4bab-be96-78dae5f6377f",
    #         "alert_tag_uuid": "0",
    #         "email_address": "test@test.com",
    #         "resend_delay": 123,
    #         "silent_period": 123,
    #         "latest_task_tag": {},
    #     }
