# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    version_update_info,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRun:
    def test_run(self, rest_client, mocker):
        rest_client.list_records.return_value = [
            dict(
                uuid="9.2.11.210763",
                description="description",
                changeLog="change log",
                buildID=210763,
                majorVersion=9,
                minorVersion=2,
                revision=11,
                timestamp=1676920067,
            )
        ]

        records = version_update_info.run(rest_client)

        assert records == [
            dict(
                uuid="9.2.11.210763",
                description="description",
                change_log="change log",
                build_id=210763,
                major_version=9,
                minor_version=2,
                revision=11,
                timestamp=1676920067,
            )
        ]
