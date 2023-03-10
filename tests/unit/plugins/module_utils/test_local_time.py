# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import local_time
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class Test_convert_utc_ts_to_local:
    @pytest.mark.parametrize(
        "utc_ts, time_zone, expected_local_tm_str",
        [
            # (1678362307, "Europe/Ljubljana", "Thu Mar  9 12:45:07 PM CET 2023"),  # Thu Mar  9 12:45:07 PM CET 2023
            # 1678352400 ==  Thu Mar 09 2023 10:00:00 GMT+0100 (Central European Standard Time)

            # https://www.timeanddate.com/news/time/europe-dst-end-2022.html
            # EU - change is on Sunday, October 30, 2022,
            # US - change is on November 6, 2022.
            # https://unixtime.org/
            # https://www.epochconverter.com/timezones

            # One timestamp, different timezones
            (1666980000, "UTC", "Fri Oct 28 2022 18:00:00 GMT+0000"),
            (1666980000, "US/Eastern", "Fri Oct 28 2022 14:00:00 GMT-0400"),
            (1666980000, "Europe/Ljubljana", "Fri Oct 28 2022 20:00:00 GMT+0200"),
            (1666980000, "America/New_York", "Fri Oct 28 2022 14:00:00 GMT-0400"),
            (1666980000, "America/New York", "Fri Oct 28 2022 14:00:00 GMT-0400"),

            # hours != minutes != seconds
            (1666980062, "Europe/Ljubljana", "Fri Oct 28 2022 20:01:02 GMT+0200"),

            # Daylight savings change in EU
            # EU summer
            (1666980000, "Europe/Ljubljana", "Fri Oct 28 2022 20:00:00 GMT+0200"),
            (1667066400, "Europe/Ljubljana", "Sat Oct 29 2022 20:00:00 GMT+0200"),
            (1667077200, "Europe/Ljubljana", "Sat Oct 29 2022 23:00:00 GMT+0200"),
            (1667080800, "Europe/Ljubljana", "Sun Oct 30 2022 00:00:00 GMT+0200"),
            (1667084400, "Europe/Ljubljana", "Sun Oct 30 2022 01:00:00 GMT+0200"),
            (1667088000, "Europe/Ljubljana", "Sun Oct 30 2022 02:00:00 GMT+0200"),
            (1667091599, "Europe/Ljubljana", "Sun Oct 30 2022 02:59:59 GMT+0200"),
            # EU winter
            (1667091600, "Europe/Ljubljana", "Sun Oct 30 2022 02:00:00 GMT+0100"),
            (1667091601, "Europe/Ljubljana", "Sun Oct 30 2022 02:00:01 GMT+0100"),
            (1667095199, "Europe/Ljubljana", "Sun Oct 30 2022 02:59:59 GMT+0100"),
            (1667095200, "Europe/Ljubljana", "Sun Oct 30 2022 03:00:00 GMT+0100"),
            (1667156400, "Europe/Ljubljana", "Sun Oct 30 2022 20:00:00 GMT+0100"),
            (1667242800, "Europe/Ljubljana", "Mon Oct 31 2022 20:00:00 GMT+0100"),
            # same timestamp in US
            (1667091599, "US/Eastern", "Sat Oct 29 2022 20:59:59 GMT-0400"),
            (1667091600, "US/Eastern", "Sat Oct 29 2022 21:00:00 GMT-0400"),
            (1667091599, "America/New York", "Sat Oct 29 2022 20:59:59 GMT-0400"),
            (1667091600, "America/New York", "Sat Oct 29 2022 21:00:00 GMT-0400"),

            # Daylight savings change in US
            # US summer
            (1667710800, "America/New York", "Sun Nov 06 2022 01:00:00 GMT-0400"),
            (1667714399, "America/New York", "Sun Nov 06 2022 01:59:59 GMT-0400"),
            # US winter
            (1667714400, "America/New York", "Sun Nov 06 2022 01:00:00 GMT-0500"),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500"),
            # same timestamp in EU
            (1667710800, "Europe/Ljubljana", "Sun Nov 06 2022 06:00:00 GMT+0100"),
            (1667714399, "Europe/Ljubljana", "Sun Nov 06 2022 06:59:59 GMT+0100"),
            (1667714400, "Europe/Ljubljana", "Sun Nov 06 2022 07:00:00 GMT+0100"),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100"),
        ],
    )
    def test_min(self, utc_ts, time_zone, expected_local_tm_str):
        local_tm, local_tm_str = local_time.convert_utc_ts_to_local(utc_ts, time_zone)
        print(f"utc_ts={utc_ts} local_tm={local_tm} local_tm_str={local_tm_str}")
        assert local_tm_str == expected_local_tm_str
        local_hour_str, local_min_str, local_sec_str = (expected_local_tm_str.split(' ')[4]).split(':')
        assert local_tm.tm_hour == int(local_hour_str, 10)
        assert local_tm.tm_min == int(local_min_str, 10)
        assert local_tm.tm_sec == int(local_sec_str, 10)


class Test_is_local_time_in_time_interval:
    @pytest.mark.parametrize(
        "utc_ts, time_zone, expected_local_tm_str, time_interval, expected_in_interval",
        [
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "22:00-05:00", True),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "22:00-05:00", False),
            # with spaces in interval
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "22:00 - 05:00", True),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "22:00 - 05:00", False),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", " 22:00 - 05:00 ", True),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", " 22:00 - 05:00 ", False),
            # inverted interval
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "05:00-22:00", False),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "05:00-22:00", True),

            # sliding interval
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "22:00-01:00", False),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "22:00-01:00", False),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "22:00-01:59", False),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "22:00-02:00", False),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "22:00-02:01", True),
            #
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "01:00-05:00", True),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "01:59-05:00", True),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "02:00-05:00", True),
            (1667718000, "America/New York", "Sun Nov 06 2022 02:00:00 GMT-0500", "02:01-05:00", False),
            #
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "22:00-07:00", False),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "22:00-07:59", False),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "22:00-08:00", False),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "22:00-08:01", True),
            #
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "07:00-10:00", True),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "07:59-10:00", True),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "08:00-10:00", True),
            (1667718000, "Europe/Ljubljana", "Sun Nov 06 2022 08:00:00 GMT+0100", "08:01-10:00", False),
        ],
    )
    def test_min(self, utc_ts, time_zone, expected_local_tm_str, time_interval, expected_in_interval):
        # I cannot read UTC timestamp/zone, so better double check expected_local_tm_str is correct
        local_tm, local_tm_str = local_time.convert_utc_ts_to_local(utc_ts, time_zone)
        assert local_tm_str == expected_local_tm_str

        in_interval = local_time.is_local_time_in_time_interval(utc_ts, time_zone, time_interval)
        assert in_interval == expected_in_interval
        inverted_time_interval = time_interval.split('-')[1] + '-' + time_interval.split('-')[0]
        in_interval = local_time.is_local_time_in_time_interval(utc_ts, time_zone, inverted_time_interval)
        assert in_interval == (not expected_in_interval)
