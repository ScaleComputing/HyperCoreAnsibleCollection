# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.time_zone import (
    TimeZone,
)
from ansible_collections.scale_computing.hypercore.plugins.modules import time_zone

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestModifyTimeZone:
    @pytest.mark.parametrize(
        ("param_zone", "rc_time_zone"),
        [("US/Eastern", "US/Eastern"), ("Europe/Ljubljana", "US/Eastern")],
    )
    def test_modify_time_zone(
        self,
        create_module,
        rest_client,
        task_wait,
        mocker,
        param_zone,
        rc_time_zone,
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0", username="admin", password="admin"
                ),
                zone=param_zone,
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.time_zone.TimeZone.get_by_uuid"
        ).return_value = TimeZone(
            uuid="test",
            time_zone=rc_time_zone,
            latest_task_tag={},
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.time_zone.TimeZone.get_state"
        )
        rest_client.create_record.return_value = {
            "taskTag": 123,
        }

        called_with_dict = dict(
            endpoint="/rest/v1/TimeZone/test",
            payload=dict(
                timeZone=param_zone,
            ),
            check_mode=False,
        )
        time_zone.modify_time_zone(module, rest_client)

        if param_zone != rc_time_zone:
            rest_client.update_record.assert_called_once_with(**called_with_dict)
        else:
            rest_client.update_record.assert_not_called()

    def test_modify_time_zone_missing_config(self, create_module, rest_client, mocker):
        with pytest.raises(errors.ScaleComputingError):
            module = create_module(
                params=dict(
                    zone="US/Eastern",
                ),
            )
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.module_utils.time_zone.TimeZone.get_by_uuid"
            ).return_value = None

            time_zone.modify_time_zone(module, rest_client)

    def test_modify_time_zone_unsupported_zone(
        self, create_module, rest_client, mocker
    ):
        with pytest.raises(errors.ScaleComputingError):
            module = create_module(
                params=dict(
                    zone="Unsupported/Zone",
                ),
            )
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.module_utils.time_zone.TimeZone.get_by_uuid"
            ).return_value = None

            time_zone.modify_time_zone(module, rest_client)


class TestMain:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )

    def test_fail(self, run_main):
        success, result = run_main(time_zone)

        assert success is False
        assert "missing required arguments: zone" in result["msg"]

    def test_params(self, run_main):
        params = dict(
            cluster_instance=self.cluster_instance,
            zone="US/Eastern",
        )
        success, result = run_main(time_zone, params)

        assert success is True
