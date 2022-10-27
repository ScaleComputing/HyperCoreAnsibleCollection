# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import io
import json
import sys

import pytest

from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlparse, parse_qs

from ansible_collections.scale_computing.hypercore.plugins.module_utils import (
    client,
    rest_client,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


def mock_list_records():
    pass

class TestCachedRestClient:
    # @pytest.mark.parametrize(
    #     "swap_query0_query1",
    #     [
    #         (None, {}),
    #         ([], {}),
    #         ([("a", "aVal"), ("b", "bVal")], {"a": "aVal", "b": "bVal"}),
    #     ],
    # )
    def test_list_records(self, mocker):
        # records = self.client.get(path=endpoint, timeout=timeout).json
        endpoint = "url1"
        data = '[{"name": "vm0"}, {"name": "vm1"}]'
        #
        # enpty query - we get all data
        query0 = None
        expected_data0 = data
        # this query should return only subset
        query1 = {"name": "vm1"}
        expected_data1 = '[{"name": "vm1"}]'

        client_obj = client.Client("https://thehost", "user", "pass")
        cached_client = rest_client.CachedRestClient(client=client_obj)
        client_mock = mocker.patch.object(cached_client.client, "get")
        client_mock.return_value = client.Response(200, data, '')

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
