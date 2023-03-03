# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    version_update_status_info,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.hypercore_version import (
    UpdateStatus,
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
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.version_update_status_info.UpdateStatus.get"
        ).return_value = UpdateStatus(
            from_build="207183",
            percent="100",
            prepare_status="",
            update_status="COMPLETE",
            update_status_details="Update Complete. Press 'Reload' to reconnect",
            usernotes="Press 'Reload' to reconnect",
            to_build="209840",
            to_version="9.1.18.209840",
        )

        record = version_update_status_info.run(rest_client)

        assert record == dict(
            from_build="207183",
            percent="100",
            prepare_status="",
            update_status="COMPLETE",
            update_status_details="Update Complete. Press 'Reload' to reconnect",
            usernotes="Press 'Reload' to reconnect",
            to_build="209840",
            to_version="9.1.18.209840",
        )
