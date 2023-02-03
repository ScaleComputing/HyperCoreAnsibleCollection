# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.time_server import (
    TimeServer,
)
from ansible_collections.scale_computing.hypercore.plugins.modules import time_server

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestModifyTimeServer:
    @pytest.mark.parametrize(
        ("param_source", "rc_host"),
        [("pool.ntp.org", "pool.ntp.org"), ("0.pool.ntp.org", "pool.ntp.org")],
    )
    def test_modify_time_server(
        self,
        create_module,
        rest_client,
        task_wait,
        mocker,
        param_source,
        rc_host,
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0", username="admin", password="admin"
                ),
                source=param_source,
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.time_server.TimeServer.get_by_uuid"
        ).return_value = TimeServer(
            uuid="test",
            host=rc_host,
            latest_task_tag={},
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.time_server.TimeServer.get_state"
        )
        rest_client.create_record.return_value = {
            "taskTag": 123,
        }

        called_with_dict = dict(
            endpoint="/rest/v1/TimeSource/test",
            payload=dict(
                host=param_source,
            ),
            check_mode=False,
        )
        time_server.modify_time_server(module, rest_client)

        if param_source != rc_host:
            rest_client.update_record.assert_called_once_with(**called_with_dict)
        else:
            rest_client.update_record.assert_not_called()

    def test_modify_time_server_missing_config(
        self, create_module, rest_client, mocker
    ):
        with pytest.raises(errors.ScaleComputingError):
            module = create_module(
                params=dict(
                    source="pool.ntp.org",
                ),
            )
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.module_utils.time_server.TimeServer.get_by_uuid"
            ).return_value = None

            time_server.modify_time_server(module, rest_client)


class TestMain:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )

    def test_fail(self, run_main):
        success, result = run_main(time_server)

        assert success is False
        assert "missing required arguments: source" in result["msg"]

    def test_params(self, run_main):
        params = dict(
            cluster_instance=self.cluster_instance,
            source="pool.ntp.org",
        )
        success, result = run_main(time_server, params)

        assert success is True
