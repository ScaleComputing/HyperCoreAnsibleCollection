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
from ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag import (
    TaskTag,
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
        with pytest.raises(AssertionError) as excinfo:
            SyslogServer.from_hypercore([])
        assert "hypercore_data dict must be non-emtpy" in str(excinfo.value)

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

    def test_is_equivalent(self):
        ss = SyslogServer(host="1.0.0.10", port=10514, protocol="udp")

        a0 = SyslogServer(host="1.0.0.10", port=10514, protocol="udp")
        # attributes not configurable via module/GUI need to be ignored
        a1 = SyslogServer(host="1.0.0.10", port=10514, protocol="udp", uuid="uuid-a1")
        a2 = SyslogServer(
            host="1.0.0.10",
            port=10514,
            protocol="udp",
            alert_tag_uuid="alert_tag_uuid-a2",
        )
        a3 = SyslogServer(
            host="1.0.0.10", port=10514, protocol="udp", resend_delay=12345
        )
        a4 = SyslogServer(
            host="1.0.0.10", port=10514, protocol="udp", silent_period=123456
        )
        a5 = SyslogServer(
            host="1.0.0.10", port=10514, protocol="udp", latest_task_tag=TaskTag()
        )
        task_tag = dict(
            createdUUID="latest_task_tag-createdUUID", taskTag="taskTag-112233"
        )
        a6 = SyslogServer(
            host="1.0.0.10", port=10514, protocol="udp", latest_task_tag=task_tag
        )

        assert ss.is_equivalent(a0)
        assert ss.is_equivalent(a1)
        assert ss.is_equivalent(a2)
        assert ss.is_equivalent(a3)
        assert ss.is_equivalent(a4)
        assert ss.is_equivalent(a5)
        assert ss.is_equivalent(a6)

        b0 = SyslogServer(host="1.0.0.11", port=10514, protocol="udp")
        b1 = SyslogServer(host="1.0.0.10", port=11514, protocol="udp")
        b2 = SyslogServer(host="1.0.0.10", port=10514, protocol="tcp")

        assert not ss.is_equivalent(b0)
        assert not ss.is_equivalent(b1)
        assert not ss.is_equivalent(b2)

    def test_lt(self):
        s0 = SyslogServer(host="1.0.0.10", port=514, protocol="udp")
        # host is sorted as string, so we have strange "09" in IP.
        s1 = SyslogServer(host="1.0.0.09", port=514, protocol="udp")
        s2 = SyslogServer(host="1.0.0.10", port=510, protocol="udp")
        s3 = SyslogServer(host="1.0.0.10", port=514, protocol="tcp")
        assert not s0 < s1  # pylint: disable=unnecessary-negation
        assert not s0 < s2  # pylint: disable=unnecessary-negation
        assert not s0 < s3  # pylint: disable=unnecessary-negation

        assert s1 < s2
        assert s1 < s3

        assert s2 < s3

    def test_sorted(self):
        servers = [
            SyslogServer(host="1.0.0.10", port=514, protocol="udp"),
            SyslogServer(host="1.0.0.09", port=514, protocol="udp"),
            SyslogServer(host="1.0.0.10", port=510, protocol="udp"),
            SyslogServer(host="1.0.0.10", port=514, protocol="tcp"),
        ]

        servers.sort()

        assert servers[0].host == "1.0.0.09"  # <--
        assert servers[0].port == 514
        assert servers[0].protocol == "udp"
        #
        assert servers[1].host == "1.0.0.10"
        assert servers[1].port == 510  # <--
        assert servers[1].protocol == "udp"
        #
        assert servers[2].host == "1.0.0.10"
        assert servers[2].port == 514
        assert servers[2].protocol == "tcp"  # <--
        #
        assert servers[3].host == "1.0.0.10"
        assert servers[3].port == 514
        assert servers[3].protocol == "udp"
