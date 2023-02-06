# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from .errors import UnexpectedAPIResponse
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.client import Client
from ..module_utils.typed_classes import TypedSupportTunnelToAnsible
from typing import Any


class SupportTunnel(PayloadMapper):
    def __init__(self, tunnel_open: str):
        self.tunnel_open = tunnel_open

    @classmethod
    def from_ansible(cls, ansible_data: Any) -> Any:
        pass

    @classmethod
    def from_hypercore(cls, hypercore_data: dict[str, str]) -> SupportTunnel:
        # There is no None check since get_record is not used (support_tunnel's api behaves different)
        return cls(
            tunnel_open=hypercore_data["tunnelOpen"],
        )

    def to_hypercore(self) -> Any:
        pass

    def to_ansible(self) -> TypedSupportTunnelToAnsible:
        return dict(
            tunnel_open=self.tunnel_open,
        )

    def __eq__(
        self, other: object
    ) -> bool:  # object instead of SupportTunnel to make mypy happy
        """
        One support_tunnel is equal to another if it has all attributes exactly the same.
        This method is used only in tests.
        """
        if not isinstance(other, SupportTunnel):
            return NotImplemented
        return self.tunnel_open == other.tunnel_open

    @classmethod
    def check_tunnel_status(cls, client: Client) -> SupportTunnel:
        response = client.get("/support-api/check")  # type: ignore
        if response.status == 200:  # get lets 404 through
            return cls.from_hypercore(response.json)
        raise UnexpectedAPIResponse(response=response)  # type: ignore

    @staticmethod
    def open_tunnel(module: AnsibleModule, client: Client) -> None:
        response = client.get(
            "/support-api/open", query={"code": module.params["code"]}
        )  # type: ignore
        if response.status != 200:  # get lets 404 through
            raise UnexpectedAPIResponse(response=response)  # type: ignore

    @staticmethod
    def close_tunnel(client: Client) -> None:
        response = client.get("/support-api/close")  # type: ignore
        if response.status != 200:  # get lets 404 through
            raise UnexpectedAPIResponse(response=response)  # type: ignore
