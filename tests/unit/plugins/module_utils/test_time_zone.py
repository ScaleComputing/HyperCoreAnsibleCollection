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

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires2.7 or higher"
)


class TestTimeServer:
    def setup_method(self):
        self.time_zone = TimeZone(
            uuid="test",
            time_zone="US/Eastern",
            latest_task_tag={},
        )
        self.from_hypercore_dict = dict(
            uuid="test",
            timeZone="US/Eastern",
            latestTaskTag={},
        )
        self.to_hypercore_dict = dict(
            uuid="test",
            timeZone="US/Eastern",
        )
        self.ansible_dict = dict(
            uuid="test",
            time_zone="US/Eastern",
            latest_task_tag={},
        )

    def test_time_zone_to_hypercore(self):
        assert self.time_zone.to_hypercore() == self.to_hypercore_dict

    def test_time_zone_from_hypercore_dict_not_empty(self):
        time_zone_from_hypercore = TimeZone.from_hypercore(self.from_hypercore_dict)
        assert self.time_zone == time_zone_from_hypercore

    def test_time_zone_from_hypercore_dict_empty(self):
        assert TimeZone.from_hypercore([]) is None

    def test_time_zone_to_ansible(self):
        assert self.time_zone.to_ansible() == self.ansible_dict

    def test_time_zone_from_ansible(self):
        time_zone_from_ansible = TimeZone.from_ansible(self.from_hypercore_dict)
        assert self.time_zone == time_zone_from_ansible

    def test_get_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(
            uuid="test",
            timeZone="US/Eastern",
            latestTaskTag={},
        )
        ansible_dict = dict(
            uuid="test",
        )
        time_zone_from_hypercore = TimeZone.get_by_uuid(ansible_dict, rest_client)
        assert time_zone_from_hypercore == self.time_zone

    def test_get_state(self, rest_client):
        rest_client.list_records.return_value = [self.from_hypercore_dict]

        result = TimeZone.get_state(rest_client)
        assert result == {
            "uuid": "test",
            "time_zone": "US/Eastern",
            "latest_task_tag": {},
        }

    def test_get_state_more_than_one_record(self, rest_client):
        with pytest.raises(errors.ScaleComputingError):
            rest_client.list_records.return_value = [
                self.from_hypercore_dict,
                self.from_hypercore_dict,
            ]
            TimeZone.get_state(rest_client)

    def test_get_state_no_record(self, rest_client):
        rest_client.list_records.return_value = []

        result = TimeZone.get_state(rest_client)
        assert result == {}
