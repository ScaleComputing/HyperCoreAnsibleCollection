# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.smtp import (
    SMTP,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires2.7 or higher"
)


class TestDNSConfig:
    def setup_method(self):
        self.smtp = SMTP(
            uuid="test",
            smtp_server="smtp-relay.gmail.com",
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
            authPassword="test123",
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
            smtp_server="smtp-relay.gmail.com",
            port=25,
            use_ssl=True,
            use_auth=True,
            auth_user="test",
            auth_password="test123",
            from_address="test@test.com",
            latest_task_tag={},
        )

    def test_dns_config_to_hypercore(self):
        assert self.smtp.to_hypercore() == self.to_hypercore_dict

    def test_dns_config_from_hypercore_dict_not_empty(self):
        smtp_from_hypercore = SMTP.from_hypercore(self.from_hypercore_dict)
        assert self.smtp == smtp_from_hypercore

    def test_dns_config_from_hypercore_dict_empty(self):
        assert SMTP.from_hypercore([]) is None

    def test_dns_config_to_ansible(self):
        assert self.smtp.to_ansible() == self.ansible_dict

    def test_dns_config_from_ansible(self):
        smtp_from_ansible = SMTP.from_ansible(self.from_hypercore_dict)
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
        assert result == {
            "uuid": "test",
            "smtp_server": "smtp-relay.gmail.com",
            "port": 25,
            "use_ssl": True,
            "use_auth": True,
            "auth_user": "test",
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
