# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from scale_computing.hc3.plugins.modules import api

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRun:
    def test_run_call_get_method(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="get",
                endpoint="/rest/v1/VirDomain",
                data=dict(),
            )
        )

        rest_client.list_records.return_value = []

        result = api.run(module, rest_client)

        rest_client.list_records.assert_called_with(
            endpoint="/rest/v1/VirDomain",
            query={},
        )

        assert result == (False, [], None)

    def test_run_call_post_method(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="post",
                endpoint="/rest/v1/VirDomain",
                data=dict(),
            )
        )

        rest_client.get_record.return_value = None
        rest_client.create_record.return_value = dict(name="newly created record")

        result = api.run(module, rest_client)

        rest_client.create_record.assert_called_with(
            endpoint="/rest/v1/VirDomain",
            check_mode=False,
            payload=dict(),
        )

        assert result == (
            True,
            dict(name="newly created record"),
            dict(
                after=dict(name="newly created record"),
                before=None,
            ),
        )

    def test_run_call_patch_method(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="patch",
                endpoint="/rest/v1/VirDomain",
                unique_id="id",
                data=dict(),
            )
        )

        rest_client.get_record.return_value = dict(name="record before")
        rest_client.update_record.return_value = dict(name="record after")

        result = api.run(module, rest_client)

        rest_client.update_record.assert_called_with(
            endpoint="/rest/v1/VirDomain",
            payload=dict(),
            check_mode=False,
        )

        assert result == (
            True,
            dict(name="record after"),
            dict(before=dict(name="record before"), after=dict(name="record after")),
        )

    def test_run_call_delete_method(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="delete",
                endpoint="/rest/v1/VirDomain",
                unique_id="id",
                data=dict(),
            )
        )

        rest_client.get_record.return_value = dict(name="Existing record")
        rest_client.delete_record.return_value = None
        result = api.run(module, rest_client)

        rest_client.delete_record.assert_called_with(
            endpoint="/rest/v1/VirDomain",
            check_mode=False,
        )

        assert result == (
            True,
            None,
            dict(before=dict(name="Existing record"), after=None),
        )

    def test_run_call_put_method(self, create_module, client):
        # TODO: Put method hasn't been implemented yet, so tests still have to be written.
        #       Harcoding value for now.
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="put",
                endpoint="/rest/v1/VirDomain",
                unique_id="id",
                data=dict(),
            )
        )

        result = api.run(module, client)
        assert result == (-1, -1, -1)


class TestGetMethod:
    def test_get_method_record_present(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="get",
                endpoint="/rest/v1/VirDomain/id",
                data=dict(),
            )
        )

        rest_client.list_records.return_value = [
            dict(name="record1"),
            dict(name="record2"),
        ]

        result = api.get_records(module, rest_client)

        rest_client.list_records.assert_called_once()
        rest_client.list_records.assert_called_with(
            endpoint="/rest/v1/VirDomain/id",
            query={},
        )

        assert result == (False, [dict(name="record1"), dict(name="record2")], None)

    def test_get_method_record_absent(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="get",
                endpoint="/rest/v1/VirDomain",
                data=dict(),
            )
        )

        rest_client.list_records.return_value = []

        result = api.get_records(module, rest_client)

        rest_client.list_records.assert_called_once()
        rest_client.list_records.assert_called_with(
            endpoint="/rest/v1/VirDomain",
            query={},
        )

        assert result == (False, [], None)


class TestPutMethod:
    def test_put_method(self, create_module, rest_client):
        # TODO: Put method hasn't been implemented yet, so tests still have to be written.
        #       Harcoding value for now.
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="put",
                endpoint="/rest/v1/VirDomain",
                unique_id="id",
                data=dict(),
            )
        )

        result = api.put_record(module, rest_client)
        assert result == (-1, -1, -1)


class TestDeleteRecord:
    def test_delete_method_record_present(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="delete",
                endpoint="/rest/v1/VirDomain/id",
                data=dict(),
            )
        )

        rest_client.get_record.return_value = dict(name="Existing record")
        rest_client.delete_record.return_value = None
        result = api.run(module, rest_client)
        rest_client.delete_record.assert_called_once()
        rest_client.delete_record.assert_called_with(
            endpoint="/rest/v1/VirDomain/id",
            check_mode=False,
        )

        assert result == (
            True,
            None,
            dict(before=dict(name="Existing record"), after=None),
        )


class TestPostMethod:
    def test_post_method(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="post",
                endpoint="/rest/v1/VirDomain",
                data=dict(),
            )
        )

        rest_client.create_record.return_value = dict(name="Created record")
        result = api.post_record(module, rest_client)

        rest_client.create_record.assert_called_with(
            endpoint="/rest/v1/VirDomain",
            check_mode=False,
            payload=dict(),
        )

        rest_client.create_record.assert_called_once()
        assert result == (
            True,
            dict(name="Created record"),
            dict(after=dict(name="Created record"), before=None),
        )

    def test_post_method_record_present(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                action="post",
                endpoint="/rest/v1/VirDomain",
                unique_id="id",
                data=dict(name="name after"),
            )
        )

        rest_client.get_record.return_value = dict(name="record to delete")
        rest_client.delete_record.return_value = None
        result = api.delete_record(module, rest_client)
        rest_client.delete_record.assert_called_once()
        assert result == (
            True,
            None,
            dict(
                before=dict(name="record to delete"),
                after=None,
            ),
        )
