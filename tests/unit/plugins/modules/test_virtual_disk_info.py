# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    virtual_disk_info,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRun:
    def test_run(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="vdisk-0",
            )
        )
        rest_client.list_records.return_value = [
            dict(
                blockSize=1048576,
                capacityBytes=104857600,
                name="vdisk-0",
                replicationFactor=2,
                totalAllocationBytes=10485760,
                uuid="vdisk-uuid",
            )
        ]

        result = virtual_disk_info.run(module, rest_client)
        rest_client.list_records.assert_called_once_with(
            "/rest/v1/VirtualDisk",
            dict(name="vdisk-0"),
        )
        assert result == [
            dict(
                name="vdisk-0",
                uuid="vdisk-uuid",
                block_size=1048576,
                size=104857600,
                replication_factor=2,
            )
        ]
