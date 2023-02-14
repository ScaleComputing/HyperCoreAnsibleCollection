# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import node_info
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRun:
    def test_run_records_present(self, rest_client):
        rest_client.list_records.return_value = [
            dict(
                uuid="51e6d073-7566-4273-9196-58720117bd7f",
                backplaneIP="10.0.0.1",
                lanIP="10.0.0.1",
                peerID=1,
            )
        ]

        result = node_info.run(rest_client)
        assert result == [
            {
                "node_uuid": "51e6d073-7566-4273-9196-58720117bd7f",
                "backplane_ip": "10.0.0.1",
                "lan_ip": "10.0.0.1",
                "peer_id": 1,
            }
        ]

    def test_run_records_absent(self, rest_client):
        rest_client.list_records.return_value = []

        result = node_info.run(rest_client)
        assert result == []
