# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.syslog_server import (
    SyslogServer,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)

HYPERCORE_PROTOCOL_TCP = "SYSLOG_PROTOCOL_TCP"
ANSIBLE_PROTOCOL_TCP = "tcp"


class TestSyslogServer:
    def setup_method(self):
        self.syslog_server = SyslogServer(
            uuid="test",
            alert_tag_uuid="0",
            host="0.0.0.0",
            port=42,
            protocol=ANSIBLE_PROTOCOL_TCP,
            resend_delay=123,
            silent_period=123,
            latest_task_tag={},
        )
        self.from_hypercore_dict = dict(
            uuid="test",
            alertTagUUID="0",
            host="0.0.0.0",
            port=42,
            protocol=HYPERCORE_PROTOCOL_TCP,
            resendDelay=123,
            silentPeriod=123,
            latestTaskTag={},
        )
        self.to_hypercore_dict = dict(
            host="0.0.0.0",
            port=42,
            protocol=ANSIBLE_PROTOCOL_TCP,
        )
        self.ansible_dict = dict(
            uuid="test",
            alert_tag_uuid="0",
            host="0.0.0.0",
            port=42,
            protocol=ANSIBLE_PROTOCOL_TCP,
            resend_delay=123,
            silent_period=123,
            latest_task_tag={},
        )

    def test_syslog_server_to_hypercore(self):
        assert self.syslog_server.to_hypercore() == self.to_hypercore_dict

    def test_syslog_server_from_hypercore_dict_not_empty(self):
        syslog_server_from_hypercore = SyslogServer.from_hypercore(
            self.from_hypercore_dict
        )
        assert self.syslog_server == syslog_server_from_hypercore

    def test_syslog_server_from_hypercore_dict_empty(self):
        assert SyslogServer.from_hypercore([]) is None

    def test_syslog_server_to_ansible(self):
        assert self.syslog_server.to_ansible() == self.ansible_dict

    def test_syslog_server_from_ansible(self):
        syslog_server_from_ansible = SyslogServer.from_ansible(self.ansible_dict)
        assert syslog_server_from_ansible == SyslogServer(
            uuid=syslog_server_from_ansible.uuid,
            host=syslog_server_from_ansible.host,
            port=syslog_server_from_ansible.port,
            protocol=syslog_server_from_ansible.protocol,
        )

    def test_get_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(**self.from_hypercore_dict)
        ansible_dict = dict(
            uuid="test",
        )
        syslog_server_from_hypercore = SyslogServer.get_by_uuid(
            ansible_dict, rest_client
        )
        assert syslog_server_from_hypercore == self.syslog_server

    def test_get_state(self, rest_client):
        rest_client.list_records.return_value = [
            self.from_hypercore_dict,
            self.from_hypercore_dict,
        ]

        expected = {
            "uuid": "test",
            "alert_tag_uuid": "0",
            "host": "0.0.0.0",
            "port": 42,
            "protocol": ANSIBLE_PROTOCOL_TCP,
            "resend_delay": 123,
            "silent_period": 123,
            "latest_task_tag": {},
        }
        result = SyslogServer.get_state(rest_client)
        print(result)

        assert result == [expected, expected]

    def test_get_state_no_record(self, rest_client):
        rest_client.list_records.return_value = []

        result = SyslogServer.get_state(rest_client)
        assert result == []

    def test_get_by_host(self, rest_client):
        rest_client.get_record.return_value = dict(**self.from_hypercore_dict)

        result = SyslogServer.get_by_host("0.0.0.0", rest_client)
        assert result == self.syslog_server
