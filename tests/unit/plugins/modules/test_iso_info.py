# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import iso_info

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRun:
    def test_run_records_present(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="ISO-image-name",
            ),
        )

        rest_client.list_records.return_value = [
            dict(
                uuid="id",
                name="ISO-test-name",
                size=8000,
                mounts=[
                    dict(vmName="vm-name-1", vmUUID="vm-uuid-1"),
                    dict(vmName="vm-name-2", vmUUID="vm-uuid-2"),
                ],
                readyForInsert=False,
                path="scribe/1234",
            )
        ]

        result = iso_info.run(module, rest_client)
        assert result == [
            {
                "mounts": [
                    {"vm_name": "vm-name-1", "vm_uuid": "vm-uuid-1"},
                    {"vm_name": "vm-name-2", "vm_uuid": "vm-uuid-2"},
                ],
                "name": "ISO-test-name",
                "path": "scribe/1234",
                "ready_for_insert": False,
                "size": 8000,
                "uuid": "id",
            }
        ]

    def test_run_records_absent(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="ISO-image-name",
            ),
        )

        rest_client.list_records.return_value = []

        result = iso_info.run(module, rest_client)
        assert result == []
