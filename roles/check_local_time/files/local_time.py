# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

import os
import time
import datetime


MY_TIME_ZONE = os.environ["MY_TIME_ZONE"]
MY_TIME_INTERVAL = os.environ["MY_TIME_INTERVAL"]


def get_local_time(time_zone: str) -> datetime.datetime:
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

    local_struct_time = time.localtime()
    local_time_str = time.strftime("%a %b %d %Y %H:%M:%S GMT%z", local_struct_time)
    local_time = datetime.datetime.strptime(
        local_time_str, "%a %b %d %Y %H:%M:%S GMT%z"
    )

    if orig_tz:
        os.environ["TZ"] = orig_tz
    else:
        os.environ.pop("TZ")
    time.tzset()

    return local_time


def is_local_time_in_time_interval(time_zone: str, time_interval: str) -> bool:
    local_time = get_local_time(time_zone)

    time_list = time_interval.split("-")
    assert len(time_list) == 2
    start_time_str = time_list[0].strip()
    end_time_str = time_list[1].strip()

    # (datatime|time).strptime("22:00", "%H:%M") - does return something near year 1900
    start_time = datetime.datetime.strptime(start_time_str, "%H:%M")
    end_time = datetime.datetime.strptime(end_time_str, "%H:%M")

    if start_time < end_time:
        print(start_time.time() <= local_time.time() < end_time.time())
    else:  # Over midnight
        print(
            local_time.time() >= start_time.time()
            or local_time.time() < end_time.time()
        )


if __name__ == "__main__":
    is_local_time_in_time_interval(MY_TIME_ZONE, MY_TIME_INTERVAL)
