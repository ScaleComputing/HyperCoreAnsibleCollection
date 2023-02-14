# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import iso
from unittest.mock import patch, mock_open
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestEnsureAbsent:
    def test_ensure_absent(self, create_module, rest_client, task_wait):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="ISO-image-name",
                state="absent",
            ),
        )

        rest_client.get_record.return_value = dict(
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
        rest_client.delete_record.return_value = None
        result = iso.ensure_absent(module, rest_client)
        rest_client.delete_record.assert_called_once_with(
            endpoint="/rest/v1/ISO/id",
            check_mode=False,
        )
        assert result == (
            True,
            [
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
            ],
            {
                "after": None,
                "before": {
                    "mounts": [
                        {"vm_name": "vm-name-1", "vm_uuid": "vm-uuid-1"},
                        {"vm_name": "vm-name-2", "vm_uuid": "vm-uuid-2"},
                    ],
                    "name": "ISO-test-name",
                    "path": "scribe/1234",
                    "ready_for_insert": False,
                    "size": 8000,
                    "uuid": "id",
                },
            },
        )


class TestEnsurePresent:
    def test_ensure_present_iso_image_present(
        self, create_module, rest_client, os_stat, task_wait
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="ISO-image-name",
                state="present",
                source="/path/to/source",
            ),
        )

        rest_client.get_record.return_value = dict(
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

        rest_client.create_record.return_value = dict(createdUUID="id")
        rest_client.put_record.return_value = None
        rest_client.update_record.return_value = dict(readyForInsert=True)
        # Comments (tjazsch): This tests gets stuck when mocking call os.stat. If this gets resolved,
        # built-in method call open(source, "rb") has to be mocked additionally

        with patch("builtins.open", mock_open(read_data="bla bla bla")):
            result = iso.ensure_present(module, rest_client)

        rest_client.create_record.assert_called_once()
        rest_client.put_record.assert_called_once()
        rest_client.update_record.assert_called_once()

        assert result == (
            True,
            [
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
            ],
            {
                "after": {
                    "mounts": [
                        {"vm_name": "vm-name-1", "vm_uuid": "vm-uuid-1"},
                        {"vm_name": "vm-name-2", "vm_uuid": "vm-uuid-2"},
                    ],
                    "name": "ISO-test-name",
                    "path": "scribe/1234",
                    "ready_for_insert": False,
                    "size": 8000,
                    "uuid": "id",
                },
                "before": None,
            },
        )

    def test_ensure_present_iso_image_present_ready_for_insert_true(
        self, create_module, rest_client
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="ISO-image-name",
                source="/path/to/source",
                state="present",
            ),
        )
        rest_client.get_record.return_value = dict(
            name="iso-image-name",
            readyForInsert=True,
            uuid="id",
            size=1234,
            mounts=[],
            path="/path/",
        )

        rest_client.create_record.assert_not_called()
        rest_client.put_record.assert_not_called()
        rest_client.update_record.assert_not_called()
        result = iso.ensure_present(module, rest_client)
        assert result == (
            False,
            [
                {
                    "mounts": [],
                    "name": "iso-image-name",
                    "path": "/path/",
                    "ready_for_insert": True,
                    "size": 1234,
                    "uuid": "id",
                }
            ],
            {},
        )
