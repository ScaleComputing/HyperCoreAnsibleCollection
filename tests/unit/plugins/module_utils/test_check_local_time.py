# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest
import datetime

from ansible_collections.scale_computing.hypercore.roles.check_local_time.files import (
    check_local_time,
)

# from ansible_collections.scale_computing.hypercore.plugins.module_utils import (
#     check_local_time,
# )

from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestCheckLocalTime:
    def test_get_local_time(self):
        local_time = check_local_time.get_local_time("Europe/Ljubljana")
        assert isinstance(local_time, datetime.datetime)

    def test_get_time_interval(self):
        start_time, end_time = check_local_time.get_time_interval("22:31-4:45")
        start_time_str = datetime.datetime.strftime(start_time, "%H:%M")
        end_time_str = datetime.datetime.strftime(end_time, "%H:%M")

        assert start_time_str == "22:31"
        assert end_time_str == "04:45"

    @pytest.mark.parametrize(
        "time_interval, expected_result",
        [
            ("22:30-1:30", "False"),
            ("6:30-08:30", "False"),
            ("12:30-13:00", "True"),
            ("1:00-12:30", "False"),
            ("1:00-12:31", "True"),
            ("22:00-12:30", "False"),
            ("22:00-12:31", "True"),
        ],
    )
    def test_is_local_time_in_time_interval(
        self, time_interval, expected_result, capfd
    ):
        local_time = datetime.datetime.now()
        local_time_constant = local_time.replace(hour=12, minute=30)

        start_time, end_time = check_local_time.get_time_interval(time_interval)
        check_local_time.is_local_time_in_time_interval(
            local_time_constant, start_time, end_time
        )
        result, err = capfd.readouterr()

        assert result.strip() == expected_result  # strip removes "\n"

    @pytest.mark.parametrize(
        "time_interval, expected_result",
        [
            ("22:30-1:30", "False"),
            ("6:30-08:30", "False"),
            ("12:30-13:00", "True"),
            ("1:00-12:30", "False"),
            ("1:00-12:31", "True"),
            ("22:00-12:30", "False"),
            ("22:00-12:31", "True"),
        ],
    )
    def test_main(self, mocker, time_interval, expected_result, capfd):
        local_time = datetime.datetime.now()
        local_time_constant = local_time.replace(hour=12, minute=30)
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.roles.check_local_time.files.check_local_time.get_local_time"
        ).return_value = local_time_constant

        check_local_time.main("Europe/Ljubljana", time_interval)
        result, err = capfd.readouterr()

        assert result.strip() == expected_result
