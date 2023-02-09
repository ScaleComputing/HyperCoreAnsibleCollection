# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils import errors
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import (
    TypedTaskTag,
    TypedOidcToAnsible,
    TypedOidcFromAnsible,
)
from typing import Union, Any


class Oidc(PayloadMapper):
    def __init__(
        self,
        uuid: Union[str, None] = None,
        client_id: Union[str, None] = None,
        config_url: Union[str, None] = None,
        certificate: Union[str, None] = None,
        shared_secret: Union[str, None] = None,  # Write-only
        scopes: Union[str, None] = None,
    ):
        self.uuid = uuid
        self.client_id = client_id
        self.config_url = config_url
        self.certificate = certificate
        self.shared_secret = shared_secret
        self.scopes = scopes

    @classmethod
    def get(cls, rest_client: RestClient) -> Union[Oidc, None]:
        result = rest_client.list_records("/rest/v1/OIDCConfig")
        if result:
            # One OIDC per cluster.
            return cls.from_hypercore(result[0])
        return None

    @classmethod
    def from_hypercore(cls, hypercore_data: dict[Any, Any]) -> Oidc:
        try:
            obj = cls()
            obj.uuid = hypercore_data["uuid"]
            obj.client_id = hypercore_data["clientID"]
            obj.certificate = hypercore_data["certificate"]
            obj.config_url = hypercore_data["configurationURL"]
            obj.scopes = hypercore_data["scopes"]
            return obj
        except KeyError as e:
            raise errors.MissingValueHypercore(e)

    @classmethod
    def from_ansible(cls, ansible_data: TypedOidcFromAnsible) -> Oidc:
        obj = cls()
        obj.client_id = ansible_data.get("client_id", None)
        obj.config_url = ansible_data.get("config_url", None)
        obj.shared_secret = ansible_data.get("shared_secret", None)
        obj.certificate = ansible_data.get("certificate", None)
        obj.scopes = ansible_data.get("scopes", None)
        return obj

    def to_hypercore(self) -> dict[Any, Any]:
        hypercore_dict = dict()
        if self.client_id:
            hypercore_dict["clientID"] = self.client_id
        if self.config_url:
            hypercore_dict["configurationURL"] = self.config_url
        if self.shared_secret:
            hypercore_dict["sharedSecret"] = self.shared_secret
        if self.certificate:
            hypercore_dict["certificate"] = self.certificate
        if self.scopes:
            hypercore_dict["scopes"] = self.scopes
        return hypercore_dict

    def to_ansible(self) -> TypedOidcToAnsible:
        return dict(
            client_id=self.client_id,
            certificate=self.certificate,
            config_url=self.config_url,
            scopes=self.scopes,
        )

    def send_create_request(self, rest_client: RestClient) -> TypedTaskTag:
        payload = self.to_hypercore()
        return rest_client.create_record("/rest/v1/OIDCConfig", payload, False)

    def send_delete_request(self, rest_client: RestClient) -> TypedTaskTag:
        return rest_client.delete_record("/rest/v1/OIDCConfig/oidcconfig_uuid", False)

    def send_update_request(self, rest_client: RestClient) -> TypedTaskTag:
        payload = self.to_hypercore()
        return rest_client.update_record(
            "/rest/v1/OIDCConfig/oidcconfig_uuid", payload, False
        )
