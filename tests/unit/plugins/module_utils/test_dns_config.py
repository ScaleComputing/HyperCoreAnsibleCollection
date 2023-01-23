# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
from unittest.mock import MagicMock

from ansible_collections.scale_computing.hypercore.plugins.module_utils.dns_config import (
    DNSConfig,
)

pytest = pytest.mark.skipif(sys.version_info < (2, 7), reason="requires2.7 or higher")


class TestDNSConfig:
    def setup_method(self):
        self.dns_config = DNSConfig(
            uuid="test",
            search_domains=["example.domain1.com", "example.domain2.com"],
            server_ips=["1.2.3.4", "5.6.7.8"],
        )
        self.hypercore_dict = dict(
            uuid="test",
            searchDomains=["example.domain1.com", "example.domain2.com"],
            serverIPs=["1.2.3.4", "5.6.7.8"],
        )
        self.ansible_dict = dict(
            uuid="test",
            search_domains=["example.domain1.com", "example.domain2.com"],
            server_ips=["1.2.3.4", "5.6.7.8"],
        )

    def test_dns_config_to_hypercore(self):
        assert self.dns_config.to_hypercore() == self.hypercore_dict

    def test_dns_config_from_hypercore_dict_not_empty(self):
        dns_config_from_hypercore = DNSConfig.from_hypercore(self.hypercore_dict)
        assert self.dns_config == dns_config_from_hypercore

    def test_dns_config_from_hypercore_dict_empty(self):
        assert DNSConfig.from_hypercore([]) is None

    def test_dns_config_to_ansible(self):
        assert self.dns_config.to_ansible() == self.ansible_dict

    def test_dns_config_from_ansible(self):
        dns_config_from_ansible = DNSConfig.from_ansible(self.ansible_dict)
        assert self.dns_config == dns_config_from_ansible

    def test_get_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(
            uuid="test",
            searchDomains=["example.domain1.com", "example.domain2.com"],
            serverIPs=["1.2.3.4", "5.6.7.8"],
        )
        ansible_dict = dict(
            uuid="test",
        )
        dns_config_from_hypercore = DNSConfig.get_by_uuid(ansible_dict, rest_client)
        assert dns_config_from_hypercore == self.dns_config
