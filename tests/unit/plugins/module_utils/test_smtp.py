# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from copy import deepcopy

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.smtp import (
    SMTP,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestSMTP:
    def setup_method(self):
        self.smtp = SMTP(
            uuid="test",
            server="smtp-relay.gmail.com",
            port=25,
            use_ssl=True,
            use_auth=True,
            auth_user="test",
            auth_password="test123",
            from_address="test@test.com",
            latest_task_tag={},
        )
        self.from_hypercore_dict = dict(
            uuid="test",
            smtpServer="smtp-relay.gmail.com",
            port=25,
            useSSL=True,
            useAuth=True,
            authUser="test",
            authPassword="",
            fromAddress="test@test.com",
            latestTaskTag={},
        )
        self.to_hypercore_dict = dict(
            smtpServer="smtp-relay.gmail.com",
            port=25,
            useSSL=True,
            useAuth=True,
            authUser="test",
            authPassword="test123",
            fromAddress="test@test.com",
        )
        self.ansible_dict = dict(
            uuid="test",
            server="smtp-relay.gmail.com",
            port=25,
            use_ssl=True,
            use_auth=True,
            auth_user="test",
            auth_password="test123",
            from_address="test@test.com",
            latest_task_tag={},
        )

    def test_smtp_to_hypercore(self):
        assert self.smtp.to_hypercore() == self.to_hypercore_dict

    def test_smtp_from_hypercore_dict_not_empty(self):
        smtp_from_hypercore = SMTP.from_hypercore(self.from_hypercore_dict)
        smtp_no_password = deepcopy(self.smtp)
        smtp_no_password.auth_password = ""
        print(f"smtp_no_password=   {smtp_no_password}")
        print(f"smtp_from_hypercore={smtp_from_hypercore}")
        assert smtp_no_password == smtp_from_hypercore

    # SMTP.get_by_uuid could get hypercore_dict=None, but does early exit.
    # SMTP.list_records could get [], but then for loop does not call .from_hypercore()
    # Test is not needed.
    # def test_smtp_from_hypercore_dict_empty(self):
    #     assert SMTP.from_hypercore([]) is None

    def test_smtp_to_ansible(self):
        print(f"self.smtp.to_ansible()={self.smtp.to_ansible()}")
        print(f"self.ansible_dict=     {self.ansible_dict}")
        assert self.smtp.to_ansible() == self.ansible_dict

    def test_smtp_from_ansible(self):
        smtp_from_ansible = SMTP.from_ansible(self.ansible_dict)
        print(f"self.smtp={self.smtp}")
        print(f"smtp_from_ansible={smtp_from_ansible}")
        assert self.smtp == smtp_from_ansible

    def test_get_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(
            uuid="test",
            smtpServer="smtp-relay.gmail.com",
            port=25,
            useSSL=True,
            useAuth=True,
            authUser="test",
            authPassword="test123",
            fromAddress="test@test.com",
            latestTaskTag={},
        )
        ansible_dict = dict(
            uuid="test",
        )
        smtp_from_hypercore = SMTP.get_by_uuid(ansible_dict, rest_client)
        assert smtp_from_hypercore == self.smtp

    def test_get_state(self, rest_client):
        rest_client.list_records.return_value = [self.from_hypercore_dict]

        result = SMTP.get_state(rest_client)
        print(f"result={result}")
        assert result == {
            "uuid": "test",
            "server": "smtp-relay.gmail.com",
            "port": 25,
            "use_ssl": True,
            "use_auth": True,
            "auth_user": "test",
            "auth_password": "",
            "from_address": "test@test.com",
            "latest_task_tag": {},
        }

    def test_get_state_more_than_one_record(self, rest_client):
        tmp_dict = self.from_hypercore_dict

        with pytest.raises(errors.ScaleComputingError):
            rest_client.list_records.return_value = [
                tmp_dict,
                tmp_dict,
            ]
            SMTP.get_state(rest_client)

    def test_get_state_no_record(self, rest_client):
        rest_client.list_records.return_value = []

        result = SMTP.get_state(rest_client)
        assert result == {}
