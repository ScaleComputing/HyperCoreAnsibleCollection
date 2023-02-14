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
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestTimeServer:
    def setup_method(self):
        self.time_server = TimeServer(
            uuid="test",
            host="pool.ntp.org",
            latest_task_tag={},
        )
        self.from_hypercore_dict = dict(
            uuid="test",
            host="pool.ntp.org",
            latestTaskTag={},
        )
        self.to_hypercore_dict = dict(
            uuid="test",
            host="pool.ntp.org",
        )
        self.ansible_dict = dict(
            uuid="test",
            host="pool.ntp.org",
            latest_task_tag={},
        )

    def test_time_server_to_hypercore(self):
        assert self.time_server.to_hypercore() == self.to_hypercore_dict

    def test_time_server_from_hypercore_dict_not_empty(self):
        time_server_from_hypercore = TimeServer.from_hypercore(self.from_hypercore_dict)
        assert self.time_server == time_server_from_hypercore

    def test_time_server_from_hypercore_dict_empty(self):
        assert TimeServer.from_hypercore([]) is None

    def test_time_server_to_ansible(self):
        assert self.time_server.to_ansible() == self.ansible_dict

    def test_time_server_from_ansible(self):
        time_server_from_ansible = TimeServer.from_ansible(self.from_hypercore_dict)
        assert self.time_server == time_server_from_ansible

    def test_get_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(
            uuid="test",
            host="pool.ntp.org",
            latestTaskTag={},
        )
        ansible_dict = dict(
            uuid="test",
        )
        time_server_from_hypercore = TimeServer.get_by_uuid(ansible_dict, rest_client)
        assert time_server_from_hypercore == self.time_server

    def test_get_state(self, rest_client):
        rest_client.list_records.return_value = [self.from_hypercore_dict]

        result = TimeServer.get_state(rest_client)
        assert result == {
            "uuid": "test",
            "host": "pool.ntp.org",
            "latest_task_tag": {},
        }

    def test_get_state_more_than_one_record(self, rest_client):
        with pytest.raises(errors.ScaleComputingError):
            rest_client.list_records.return_value = [
                self.from_hypercore_dict,
                self.from_hypercore_dict,
            ]
            TimeServer.get_state(rest_client)

    def test_get_state_no_record(self, rest_client):
        rest_client.list_records.return_value = []

        result = TimeServer.get_state(rest_client)
        assert result == {}
