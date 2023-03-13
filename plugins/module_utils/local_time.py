# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

import os
import time
from typing import Tuple


MIN_PYTHON_VERSION = (3, 8)


def convert_utc_ts_to_local(
    utc_ts: int, time_zone: str
) -> Tuple[time.struct_time, str]:
    # https://docs.python.org/3/library/time.html#time.tzset
    # There should be no space in zone name.
    # We have files like
    #   /usr/share/zoneinfo/America/New_York
    #   /usr/share/zoneinfo/America/North_Dakota/New_Salem
    time_zone_nospace = time_zone.replace(" ", "_")

    orig_tz = os.environ.get("TZ")
    os.environ["TZ"] = time_zone_nospace
    time.tzset()
    # print(f"time tzname={time.tzname} timezone={time.timezone} altzone={time.altzone} daylight={time.daylight}")

    local_tm = time.localtime(utc_ts)
    local_tm_str = time.strftime("%a %b %d %Y %H:%M:%S GMT%z", local_tm)

    if orig_tz:
        os.environ["TZ"] = orig_tz
    else:
        os.environ.pop("TZ")
    time.tzset()

    return local_tm, local_tm_str


def _struct_time_to_seconds_in_day(struct_tm: time.struct_time) -> int:
    return struct_tm.tm_sec + 60 * (struct_tm.tm_min + 60 * struct_tm.tm_hour)


def is_local_time_in_time_interval(
    utc_ts: int, time_zone: str, time_interval: str
) -> bool:
    local_time_tm, local_time_str = convert_utc_ts_to_local(utc_ts, time_zone)

    time_list = time_interval.split("-")
    assert len(time_list) == 2
    start_time_str = time_list[0].strip()
    end_time_str = time_list[1].strip()

    # (datatime|time).strptime("22:00", "%H:%M") - does return something near year 1900
    start_time_tm = time.strptime(start_time_str, "%H:%M")
    end_time_tm = time.strptime(end_time_str, "%H:%M")
    start_time = _struct_time_to_seconds_in_day(start_time_tm)
    end_time = _struct_time_to_seconds_in_day(end_time_tm)
    local_time = _struct_time_to_seconds_in_day(local_time_tm)

    if start_time < end_time:
        return start_time <= local_time < end_time
    else:  # Over midnight
        return local_time >= start_time or local_time < end_time
