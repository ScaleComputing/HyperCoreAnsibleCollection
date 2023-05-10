# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
import datetime
from datetime import date

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot import (
    VMSnapshot,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


# Test calculate_data() static method.
class TestCalculateDate:
    @pytest.mark.parametrize(
        "days, expected_output",
        [
            (1, (datetime.datetime.today().date() + datetime.timedelta(days=1))),
            (0, None),
            (None, None),
        ],
    )
    def test_calculate_date(self, days, expected_output):
        result = VMSnapshot.calculate_date(days)
        if result:  # If not None or 0 convert to date.
            result = date.fromtimestamp(result)
        assert result == expected_output
