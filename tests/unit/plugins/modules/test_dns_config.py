# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
from unittest.mock import MagicMock

from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.dns_config import (
    DNSConfig,
)
from ansible_collections.scale_computing.hypercore.plugins.modules import dns_config

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestModifyDNSConfig:
    @pytest.mark.parametrize(
        ("api_entry_list", "module_entry_list", "state", "expected"),
        [
            (["a", "b", "c"], ["d", "e"], "set", (["d", "e"], True)),
            (["a", "b", "c"], None, "set", (["a", "b", "c"], False)),
            (["a", "b", "c"], None, "before", (["a", "b", "c"], False)),
            (["a", "b", "c"], None, "after", (["a", "b", "c"], False)),
            (["a", "b", "c"], [], "set", ([], True)),
            (["a", "b", "c"], ["a", "b", "c"], "set", (["a", "b", "c"], False)),
            (["a", "b", "c"], ["a", "b", "c"], "before", (["a", "b", "c"], False)),
            (["a", "b", "c"], ["a", "b", "c"], "after", (["a", "b", "c"], False)),
            (["a", "b", "c"], ["d", "e"], "before", (["d", "e", "a", "b", "c"], True)),
            (["a", "b", "c"], ["d", "e"], "after", (["a", "b", "c", "d", "e"], True)),
            (
                ["a", "b", "c"],
                ["d", "d", "e"],
                "before",
                (["d", "e", "a", "b", "c"], True),
            ),
            (["a", "b", "c"], ["b", "a"], "before", (["b", "a", "c"], True)),
            ([], ["a", "b", "c"], "before", (["a", "b", "c"], True)),
            ([], ["a", "b", "c"], "after", (["a", "b", "c"], True)),
        ],
    )
    def test_build_entry_list(self, api_entry_list, module_entry_list, state, expected):
        actual = dns_config.build_entry_list(api_entry_list, module_entry_list, state)
        assert actual == expected

    @pytest.mark.parametrize(
        (
            "rc_search_domains",
            "rc_server_ips",
            "search_domains",
            "dns_servers",
            "state",
            "expected_search_domains",
            "expected_server_ips",
            "expected_action_called",
        ),
        [
            (
                [],
                [],
                ["test1", "test2"],
                ["1.2.3.4", "5.6.7.8"],
                "set",
                ["test1", "test2"],
                ["1.2.3.4", "5.6.7.8"],
                "create",
            ),
            (
                [],
                [],
                ["test1", "test2"],
                ["1.2.3.4", "5.6.7.8"],
                "before",
                ["test1", "test2"],
                ["1.2.3.4", "5.6.7.8"],
                "update",
            ),
            (
                ["test1", "test2"],
                ["1.2.3.4"],
                ["test3"],
                ["5.6.7.8"],
                "before",
                ["test3", "test1", "test2"],
                ["5.6.7.8", "1.2.3.4"],
                "update",
            ),
            (
                ["test1", "test2"],
                ["1.2.3.4"],
                ["test3"],
                ["5.6.7.8"],
                "after",
                ["test1", "test2", "test3"],
                ["1.2.3.4", "5.6.7.8"],
                "update",
            ),
            (["test1", "test2"], ["1.2.3.4"], [], [], "set", [], [], "create"),
            (
                ["test1", "test2"],
                ["1.2.3.4"],
                [],
                None,
                "set",
                [],
                ["1.2.3.4"],
                "create",
            ),
            (
                ["test1", "test2"],
                ["1.2.3.4"],
                ["test1", "test2"],
                ["1.2.3.4"],
                "set",
                ["test1", "test2"],
                ["1.2.3.4"],
                None,
            ),
        ],
    )
    def test_modify_dns_config(
        self,
        create_module,
        rest_client,
        task_wait,
        mocker,
        rc_search_domains,
        rc_server_ips,
        search_domains,
        dns_servers,
        state,
        expected_search_domains,
        expected_server_ips,
        expected_action_called,
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0", username="admin", password="admin"
                ),
                search_domains=search_domains,
                dns_servers=dns_servers,
                state=state,
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.dns_config.DNSConfig.get_by_uuid"
        ).return_value = DNSConfig(
            uuid="test",
            search_domains=rc_search_domains,
            server_ips=rc_server_ips,
            latest_task_tag={},
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.dns_config.DNSConfig.get_state"
        )
        rest_client.create_record.return_value = {
            "taskTag": 123,
        }

        called_with_dict = dict(
            endpoint="/rest/v1/DNSConfig/test",
            payload=dict(
                searchDomains=expected_search_domains, serverIPs=expected_server_ips
            ),
            check_mode=False,
        )
        dns_config.modify_dns_config(module, rest_client)
        if expected_action_called == "create":
            rest_client.create_record.assert_called_once_with(**called_with_dict)
            rest_client.update_record.assert_not_called()
        elif expected_action_called == "update":
            rest_client.create_record.assert_not_called()
            rest_client.update_record.assert_called_once_with(**called_with_dict)
        else:
            rest_client.create_record.assert_not_called()
            rest_client.update_record.assert_not_called()

    def test_modify_dns_config_missing_config(self, create_module, rest_client, mocker):
        with pytest.raises(errors.ScaleComputingError):
            module = create_module(
                params=dict(
                    cluster_instance=dict(
                        host="https://0.0.0.0", username="admin", password="admin"
                    ),
                    search_domains=[],
                    dns_servers=[],
                    state="set",
                )
            )
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.module_utils.dns_config.DNSConfig.get_by_uuid"
            ).return_value = None

            dns_config.modify_dns_config(module, rest_client)


class TestMain:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )

    def test_fail(self, run_main):
        success, result = run_main(dns_config)

        assert success is False
        assert "missing required arguments: state" in result["msg"]

    @pytest.mark.parametrize(
        ("state",),
        [
            ("set",),
            ("before",),
            ("after",),
        ],
    )
    def test_required_one_of(self, run_main, state):
        params = dict(
            cluster_instance=self.cluster_instance,
            dns_config=None,
            search_domains=None,
            state=state,
        )
        success, result = run_main(dns_config, params)

        assert success is False
        assert result["msg"]

    @pytest.mark.parametrize(
        ("state", "dns_servers", "search_domains"),
        [
            # Test with search_domains param not set
            ("set", [], None),
            ("before", [], None),
            ("after", [], None),
            # Test with dns_servers param not set
            ("set", None, []),
            ("before", None, []),
            ("after", None, []),
            # Test with both all params set
            ("set", [], []),
            ("before", [], []),
            ("after", [], []),
        ],
    )
    def test_params(self, run_main, state, dns_servers, search_domains):
        params = dict(
            cluster_instance=self.cluster_instance,
            dns_servers=dns_servers,
            search_domains=search_domains,
            state=state,
        )
        success, result = run_main(dns_config, params)

        assert success is True
