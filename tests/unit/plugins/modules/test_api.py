# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import api

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


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

        assert result == (False, [dict(name="record1"), dict(name="record2")])

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

        assert result == (False, [])


class TestPutMethod:
    def test_put_method(self, create_module, rest_client, mocker):
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
                source="this-source",
                data=dict(),
            )
        )
        mocker.patch("builtins.open", mocker.mock_open(read_data="this-data"))
        rest_client.put_record.return_value = "this-value"
        result = api.put_record(module, rest_client)
        assert result == (True, "this-value")


class TestDeleteRecord:
    def test_delete_method_record_present(self, create_module, rest_client, task_wait):
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
        rest_client.delete_record.return_value = {
            "taskTag": "1234",
            "createdUUID": "deleted-id",
        }
        result = api.run(module, rest_client)
        rest_client.delete_record.assert_called_once()
        rest_client.delete_record.assert_called_with(
            endpoint="/rest/v1/VirDomain/id",
            check_mode=False,
        )

        assert result == (True, {"taskTag": "1234", "createdUUID": "deleted-id"})

    def test_delete_method_record_absent(self, create_module, rest_client, task_wait):
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

        rest_client.get_record.return_value = None
        result = api.run(module, rest_client)
        rest_client.delete_record.assert_not_called()
        assert result == (False, dict())


class TestPostMethod:
    def test_post_method(self, create_module, rest_client, task_wait):
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

        rest_client.create_record.return_value = {
            "taskTag": "1234",
            "createdUUID": "deleted-id",
        }
        result = api.post_record(module, rest_client)

        rest_client.create_record.assert_called_with(
            endpoint="/rest/v1/VirDomain",
            check_mode=False,
            payload=dict(),
        )
        rest_client.create_record.assert_called_once()
        assert result == (True, {"createdUUID": "deleted-id", "taskTag": "1234"})
