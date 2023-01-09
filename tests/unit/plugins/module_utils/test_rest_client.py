# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import (
    rest_client,
    errors,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.client import (
    Response,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestTableListRecords:
    def test_empty_response(self, client):
        client.get.return_value = Response(
            200, '{"result": []}', {"X-Total-Count": "0"}
        )
        t = rest_client.RestClient(client)

        records = t.list_records("my_table")

        assert ["result"] == records
        client.get.assert_called_once_with(path="my_table", timeout=None)

    def test_non_empty_response(self, client):
        client.get.return_value = Response(
            200, '{"result": [{"a": 3, "b": "sys_id"}]}', {"X-Total-Count": "1"}
        )
        t = rest_client.RestClient(client)

        records = t.list_records("my_table")

        assert records == ["result"]

    def test_query_passing(self, client):
        client.get.return_value = Response(
            200, '{"result": []}', {"X-Total-Count": "0"}
        )
        t = rest_client.RestClient(client)

        t.list_records("my_table", dict(a="b"))

        client.get.assert_called_once_with(
            path="my_table",
            timeout=None,
        )


class TestTableGetRecord:
    def test_zero_matches(self, client):
        client.get.return_value = Response(
            200, '{"result": []}', {"X-Total-Count": "0"}
        )
        t = rest_client.RestClient(client)

        assert t.get_record("my_table", dict(our="query")) is None

    def test_zero_matches_fail(self, client):
        client.get.return_value = Response(
            200, '{"result": []}', {"X-Total-Count": "0"}
        )
        t = rest_client.RestClient(client)

        with pytest.raises(errors.ScaleComputingError, match="No"):
            t.get_record("my_table", dict(our="query"), must_exist=True)


class TestTableCreateRecord:
    def test_normal_mode(self, client):
        client.post.return_value = Response(201, '{"result": {"a": 3, "b": "sys_id"}}')
        t = rest_client.RestClient(client)

        record = t.create_record("my_table", dict(a=4), False)

        assert {"result": {"a": 3, "b": "sys_id"}} == record
        client.post.assert_called_with(
            "my_table",
            dict(a=4),
            query={},
            timeout=None,
        )

    def test_check_mode(self, client):
        client.post.return_value = Response(201, '{"result": {"a": 3, "b": "sys_id"}}')
        t = rest_client.RestClient(client)

        result = t.create_record("my_table", dict(a=4), True)

        assert result == dict(
            createdUUID="0000000000",
            taskTag="00000",
        )
        client.post.assert_not_called()


class TestTableUpdateRecord:
    def test_normal_mode(self, client):
        client.patch.return_value = Response(200, '{"result": {"a": 3, "b": "sys_id"}}')
        t = rest_client.RestClient(client)
        record = t.update_record("my_table/id", dict(a=4), False)

        assert {"result": {"a": 3, "b": "sys_id"}} == record
        client.patch.assert_called_with(
            "my_table/id",
            dict(a=4),
            query=dict(),
            timeout=None,
        )

    def test_check_mode(self, client):
        client.patch.return_value = Response(200, '{"result": {"a": 3, "b": "sys_id"}}')
        t = rest_client.RestClient(client)
        result = t.update_record("my_table", dict(a=4), True)
        assert result == dict(
            createdUUID="0000000000",
            taskTag="00000",
        )
        client.patch.assert_not_called()


class TestTableDeleteRecord:
    def test_normal_mode(self, client):
        client.delete.return_value = Response(
            204, '{"result": {"a": 3, "b": "sys_id"}}'
        )
        t = rest_client.RestClient(client)

        t.delete_record("my_table/id", check_mode=False)

        client.delete.assert_called_with("my_table/id", timeout=None)

    def test_check_mode(self, client):
        client.delete.return_value = Response(204, "")
        t = rest_client.RestClient(client)
        t.delete_record("my_table/id", True)
        client.delete.assert_not_called()


class TestTablePutRecord:
    def test_normal_mode(self, client):
        client.put.return_value = Response(204, '{"result": {"a": 3, "b": "sys_id"}}')
        t = rest_client.RestClient(client)

        t.put_record(
            endpoint="my_table/id",
            payload=None,
            check_mode=False,
            timeout=None,
            binary_data=None,
            headers=None,
        )

        client.put.assert_called_with(
            "my_table/id",
            data=None,
            query=None,
            timeout=None,
            binary_data=None,
            headers=None,
        )
