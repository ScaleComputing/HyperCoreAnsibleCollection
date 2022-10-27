# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import (
    client,
    rest_client,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestCachedRestClient:
    @pytest.mark.parametrize(
        "swap_query_order",
        [
            (False),
            (True),
        ],
    )
    def test_list_records(self, mocker, swap_query_order):
        endpoint = "url1"
        data = '[{"name": "vm0"}, {"name": "vm1"}]'
        #
        # enpty query - we get all data
        query0 = None
        expected_data0 = data
        # this query should return only subset
        query1 = {"name": "vm1"}
        expected_data1 = '[{"name": "vm1"}]'

        if swap_query_order:
            # First will be executed query with filtering
            query1, query0 = query0, query1
            expected_data1, expected_data0 = expected_data0, expected_data1

        client_obj = client.Client("https://thehost", "user", "pass")
        cached_client = rest_client.CachedRestClient(client=client_obj)
        client_mock = mocker.patch.object(cached_client.client, "get")
        client_mock.return_value = client.Response(200, data, "")

        # on first call, we get something back
        records = cached_client.list_records(endpoint, query0)
        assert records == json.loads(expected_data0)
        assert client_mock.call_count == 1

        # call_count is still 1
        records = cached_client.list_records(endpoint, query0)
        assert records == json.loads(expected_data0)
        assert client_mock.call_count == 1

        # now filter
        records = cached_client.list_records(endpoint, query1)
        assert records == json.loads(expected_data1)
        assert client_mock.call_count == 1

        # now filter - again
        records = cached_client.list_records(endpoint, query1)
        assert records == json.loads(expected_data1)
        assert client_mock.call_count == 1

    def test_list_records_different_endpoint(self, mocker):
        # Check calling with different endpoint does return different data
        endpoint0 = "vms"
        endpoint1 = "disks"
        data0 = '[{"name": "vm0"}]'
        data1 = '[{"disk_type": "ide"}]'

        def mockup_client_get(path, timeout):
            if path == endpoint0:
                return client.Response(200, data0, "")
            else:
                return client.Response(200, data1, "")

        client_obj = client.Client("https://thehost", "user", "pass")
        cached_client = rest_client.CachedRestClient(client=client_obj)
        client_mock = mocker.patch.object(cached_client.client, "get")
        client_mock.side_effect = mockup_client_get

        # on first call, we get something back
        records = cached_client.list_records(endpoint0, None)
        assert records == json.loads(data0)
        assert client_mock.call_count == 1

        # on second call, we get something else back
        records = cached_client.list_records(endpoint1, None)
        assert records == json.loads(data1)
        # and one extra HTTP request was needed
        assert client_mock.call_count == 2

        # try both endpoints once more
        records = cached_client.list_records(endpoint0, None)
        assert records == json.loads(data0)
        assert client_mock.call_count == 2
        #
        records = cached_client.list_records(endpoint1, None)
        assert records == json.loads(data1)
        assert client_mock.call_count == 2

    def test_list_records_empty_response(self, mocker):
        # API might return "[]" as responses
        endpoint = "vms"
        data = "[]"

        client_obj = client.Client("https://thehost", "user", "pass")
        cached_client = rest_client.CachedRestClient(client=client_obj)
        client_mock = mocker.patch.object(cached_client.client, "get")
        client_mock.return_value = client.Response(200, data, "")

        # first call
        records = cached_client.list_records(endpoint, None)
        assert records == []
        assert client_mock.call_count == 1

        # second call - should be cached too
        records = cached_client.list_records(endpoint, None)
        assert records == []
        assert client_mock.call_count == 1
