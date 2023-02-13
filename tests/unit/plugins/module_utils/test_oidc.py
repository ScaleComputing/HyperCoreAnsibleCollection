# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc import (
    Oidc,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestGet:
    def test_get_when_oidc_not_exist(self, rest_client) -> None:
        rest_client.list_records.return_value = []
        result = Oidc.get(rest_client)
        assert result is None

    def test_get_when_oidc_exist(self, rest_client) -> None:
        rest_client.list_records.return_value = [
            dict(
                uuid="id",
                clientID="this-client",
                configurationURL="this-config-url",
                certificate="this-certificate",
                scopes="this-scopes",
            )
        ]
        result = Oidc.get(rest_client)
        assert isinstance(result, Oidc) is True
        assert result.uuid == "id"
        assert result.client_id == "this-client"
        assert result.config_url == "this-config-url"
        assert result.certificate == "this-certificate"
        assert result.scopes == "this-scopes"


class TestFromAnsible:
    def test_from_ansible_oidc(self) -> None:
        data = dict(
            client_id="bla",
            shared_secret="doubleBLA",
            certificate="TripleBLA",
            config_url="QuadrupleBLA",
            scopes="scopes",
        )
        result = Oidc.from_ansible(ansible_data=data)
        assert isinstance(result, Oidc) is True
        assert result.client_id == data["client_id"]
        assert result.shared_secret == data["shared_secret"]
        assert result.certificate == data["certificate"]
        assert result.config_url == data["config_url"]
        assert result.scopes == data["scopes"]


class TestFromHypercore:
    def test_create_from_hypercore_oidc(self) -> None:
        data = dict(
            uuid="id",
            clientID="this-client-id",
            certificate="this-certificate",
            configurationURL="this-config-url",
            scopes="this-scopes",
        )
        result = Oidc.from_hypercore(hypercore_data=data)
        assert isinstance(result, Oidc) is True
        assert result.uuid == "id"
        assert result.client_id == "this-client-id"
        assert result.certificate == "this-certificate"
        assert result.config_url == "this-config-url"
        assert result.scopes == "this-scopes"


class TestToAnsible:
    def test_data_to_ansible_registration(self) -> None:
        oidc_obj = Oidc(
            client_id="bla",
            certificate="doubleBLA",
            scopes="tripleBLA",
            config_url="this_config",
            shared_secret="this_secret",
        )
        result = oidc_obj.to_ansible()
        assert isinstance(result, dict)
        assert result == dict(
            client_id="bla",
            certificate="doubleBLA",
            scopes="tripleBLA",
            config_url="this_config",
        )


class TestToHypercore:
    def test_to_hypercore_oidc(self) -> None:
        oidc_obj = Oidc(
            client_id="bla",
            certificate="doubleBLA",
            scopes="tripleBLA",
            config_url="this_config",
            shared_secret="this_secret",
        )
        result = oidc_obj.to_hypercore()
        assert isinstance(result, dict)
        assert result == dict(
            clientID="bla",
            configurationURL="this_config",
            sharedSecret="this_secret",
            certificate="doubleBLA",
            scopes="tripleBLA",
        )


class TestSendRequest:
    def test_send_create_request_oidc(self, rest_client) -> None:
        rest_client.create_record.return_value = {}
        oidc_obj = Oidc(
            client_id="bla",
            config_url="doubleBLA",
            certificate="tripleBLA",
            shared_secret="quadrupleBLA",
            scopes="blabla",
        )
        result = oidc_obj.send_create_request(rest_client)
        assert isinstance(result, dict)
        assert result == dict()

    def test_send_update_request_oidc(self, rest_client) -> None:
        rest_client.update_record.return_value = {}
        oidc_obj = Oidc(
            client_id="bla",
            config_url="doubleBLA",
            certificate="tripleBLA",
            shared_secret="quadrupleBLA",
            scopes="blabla",
        )
        result = oidc_obj.send_update_request(rest_client)
        assert isinstance(result, dict)
        assert result == dict()
