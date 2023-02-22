# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

from unittest import mock
import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.syslog_server import (
    SyslogServer,
)
from ansible_collections.scale_computing.hypercore.plugins.modules import syslog_server

from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


UDP = "SYSLOG_PROTOCOL_UDP"
TCP = "SYSLOG_PROTOCOL_TCP"


class TestModifySyslogServer:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )
        self.magic = mock.MagicMock()

    @pytest.mark.parametrize(("protocol", "expected"), [("udp", UDP), ("tcp", TCP)])
    def test_get_protocol(self, protocol, expected):
        result = syslog_server.get_protocol(protocol)
        assert result == expected

    def test_create_syslog_server(
        self,
        create_module,
        rest_client,
        task_wait,
        mocker,
    ):
        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                host="0.0.0.0",
                port=514,
                protocol="udp",
                state="present",
            )
        )

        expected_return = (
            True,
            dict(
                uuid="test",
                alert_tag_uuid="0",
                host="0.0.0.0",
                port=42,
                protocol=UDP,
                resend_delay=123,
                silent_period=123,
                latest_task_tag={},
            ),
        )

        task_tag = {
            "taskTag": 123,
            "createdUUID": "test",
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.syslog_server.SyslogServer.get_by_uuid"
        ).return_value = SyslogServer(**expected_return[1])
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.syslog_server.SyslogServer.get_by_host"
        ).return_value = None
        rest_client.create_record.return_value = task_tag

        called_with_dict = dict(
            rest_client=rest_client,
            payload=dict(host="0.0.0.0", port=514, protocol=UDP),
            check_mode=False,
        )

        changed, record, diff = syslog_server.create_syslog_server(module, rest_client)
        SyslogServer.create = mock.create_autospec(SyslogServer.create)
        syslog_server.create_syslog_server(module, rest_client)

        SyslogServer.create.assert_called_once_with(**called_with_dict)

        assert changed == expected_return[0]
        assert record == expected_return[1]  # after

    @pytest.mark.parametrize(
        ("host", "host_new", "port", "protocol", "expected"),
        [
            ("0.0.0.0", "1.2.3.4", None, None, ("1.2.3.4", 514, UDP)),
            ("0.0.0.0", "1.2.3.4", 42, "tcp", ("1.2.3.4", 42, TCP)),
            ("0.0.0.0", "0.0.0.0", 42, None, ("0.0.0.0", 42, UDP)),
            ("0.0.0.0", "0.0.0.0", None, "tcp", ("0.0.0.0", 514, TCP)),
            ("0.0.0.0", "0.0.0.0", 42, "tcp", ("0.0.0.0", 42, TCP)),
        ],
    )
    def test_build_update_payload(
        self, create_module, host, host_new, port, protocol, expected
    ):
        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                host=host,
                host_new=host_new,
                port=port,
                protocol=protocol,
                state="present",
            )
        )
        if not port:
            module.params["port"] = 514
        if not protocol:
            module.params["protocol"] = "udp"

        _syslog_server = SyslogServer(
            host=host,
            port=514,
            protocol=UDP,
        )

        result = syslog_server.build_update_payload(module, _syslog_server)
        print("result:", result)
        assert result == dict(
            host=expected[0],
            port=expected[1],
            protocol=expected[2],
        )

    @pytest.mark.parametrize(
        (
            "rc_host",
            "rc_port",
            "rc_protocol",
            "host_param",
            "host_new_param",
            "port_param",
            "protocol_param",
            "expected_host",
            "expected_port",
            "expected_protocol",
            "expected_change",
        ),
        [
            (
                # RC
                "0.0.0.0",
                42,
                UDP,
                # PARAMS
                "0.0.0.0",
                "1.2.3.4",
                None,
                None,
                # EXPECTED
                "1.2.3.4",
                42,
                UDP,
                True,
            ),
            (
                # RC
                "0.0.0.0",
                42,
                UDP,
                # PARAMS
                "0.0.0.0",
                "0.0.0.0",
                None,
                None,
                # EXPECTED
                "0.0.0.0",
                42,
                UDP,
                False,
            ),
            (
                # RC
                None,
                None,
                None,
                # PARAMS
                "0.0.0.0",
                "1.2.3.4",
                None,
                None,
                # EXPECTED
                None,
                None,
                None,
                False,
            ),
            (
                # RC
                "1.2.3.4",
                42,
                UDP,
                # PARAMS
                "0.0.0.0",
                "1.2.3.4",
                None,
                None,
                # EXPECTED
                "1.2.3.4",
                42,
                UDP,
                False,
            ),
            (
                # RC
                "0.0.0.0",
                42,
                UDP,
                # PARAMS
                "0.0.0.0",
                "0.0.0.0",
                32,
                "tcp",
                # EXPECTED
                "0.0.0.0",
                32,
                TCP,
                True,
            ),
        ],
    )
    def test_update_syslog_server(
        self,
        create_module,
        rest_client,
        task_wait,
        mocker,
        rc_host,
        rc_port,
        rc_protocol,
        host_param,
        host_new_param,
        port_param,
        protocol_param,
        expected_host,
        expected_port,
        expected_protocol,
        expected_change,
    ):
        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                host=host_param,
                host_new=host_new_param,
                port=port_param,
                protocol=protocol_param,
                state="present",
            )
        )

        if not port_param:
            module.params["port"] = 514
        if not protocol_param:
            module.params["protocol"] = "udp"

        task_tag = {
            "taskTag": 123,
        }

        if rc_host is None and rc_protocol is None and rc_port is None:
            rc_syslog_server = None
        else:
            rc_syslog_server = SyslogServer(
                uuid="test",
                alert_tag_uuid="0",
                host=rc_host,
                port=rc_port,
                protocol=rc_protocol,
                resend_delay=123,
                silent_period=123,
                latest_task_tag={},
            )

        expected_syslog_dict = dict(
            uuid="test",
            alert_tag_uuid="0",
            host=expected_host,
            port=expected_port,
            protocol=expected_protocol,
            resend_delay=123,
            silent_period=123,
            latest_task_tag={},
        )

        if not expected_host and not expected_port and not expected_protocol:
            expected_syslog_dict = {}
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.module_utils.syslog_server.SyslogServer.get_by_host"
            ).return_value = rc_syslog_server
        else:
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.module_utils.syslog_server.SyslogServer.get_by_host"
            ).return_value = SyslogServer(**expected_syslog_dict)
        rest_client.update_record.return_value = task_tag

        called_with_dict = dict(
            rest_client=rest_client,
            payload=dict(
                host=expected_host, port=expected_port, protocol=expected_protocol
            ),
            check_mode=False,
        )

        SyslogServer.update = mock.create_autospec(SyslogServer.update)
        changed, record, diff = syslog_server.update_syslog_server(
            rc_syslog_server, module, rest_client
        )
        if not rc_syslog_server:
            old_payload = None
        else:
            old_payload = rc_syslog_server.to_hypercore()

        if (not old_payload) or called_with_dict.get("payload") == old_payload:
            SyslogServer.update.assert_not_called()
        else:
            SyslogServer.update.assert_called_once_with(
                rc_syslog_server, **called_with_dict
            )

        print("record:", record)
        print("expect:", expected_syslog_dict)

        assert changed == expected_change
        assert record == expected_syslog_dict

    @pytest.mark.parametrize(
        ("rc_syslog_server", "host", "expected_return"),
        [
            (None, "0.0.0.0", (False, {})),
            (
                SyslogServer(
                    uuid="test",
                    alert_tag_uuid="0",
                    host="0.0.0.0",
                    port=42,
                    protocol="protocol",
                    resend_delay=123,
                    silent_period=123,
                    latest_task_tag={},
                ),
                "0.0.0.0",
                (True, {}),
            ),
        ],
    )
    def test_delete_syslog_server(
        self,
        create_module,
        rest_client,
        task_wait,
        mocker,
        rc_syslog_server,
        host,
        expected_return,
    ):
        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                host=host,
                state="absent",
            )
        )
        task_tag = {
            "taskTag": 123,
        }
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.syslog_server.SyslogServer.get_by_host"
        ).return_value = rc_syslog_server
        rest_client.update_record.return_value = task_tag

        called_with_dict = dict(
            rest_client=rest_client,
            check_mode=False,
        )

        changed, record, diff = syslog_server.delete_syslog_server(
            rc_syslog_server, module, rest_client
        )

        SyslogServer.delete = mock.create_autospec(SyslogServer.delete)
        syslog_server.delete_syslog_server(rc_syslog_server, module, rest_client)
        if rc_syslog_server:
            SyslogServer.delete.assert_called_once_with(
                rc_syslog_server, **called_with_dict
            )
        else:
            SyslogServer.delete.assert_not_called()

        assert changed == expected_return[0]
        assert record == expected_return[1]


class TestMain:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )

    def test_fail(self, run_main):
        success, result = run_main(syslog_server)

        print(result["msg"])

        assert success is False
        assert (
            "missing required arguments: state, host" in result["msg"]
            or "missing required arguments: host, state" in result["msg"]
        )

    @pytest.mark.parametrize(
        ("host", "host_new", "port", "protocol", "state"),
        [
            ("0.0.0.0", None, None, None, "present"),
            ("0.0.0.0", "1.2.3.4", None, None, "present"),
            ("0.0.0.0", "1.2.3.4", 42, "tcp", "present"),
            ("0.0.0.0", None, None, None, "absent"),
        ],
    )
    def test_params(
        self,
        run_main,
        host,
        host_new,
        port,
        protocol,
        state,
    ):
        params = dict(
            cluster_instance=self.cluster_instance,
            host=host,
            host_new=host_new,
            port=port,
            protocol=protocol,
            state=state,
        )

        # put them to default if None
        if not port:
            params["port"] = 514
        if not protocol:
            params["protocol"] = "udp"

        success, result = run_main(syslog_server, params)

        print(result)

        assert success is True
