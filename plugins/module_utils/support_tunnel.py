# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.client import Client
from ..module_utils.typed_classes import TypedSupportTunnelToAnsible
from typing import Any, Union, Optional


class SupportTunnel(PayloadMapper):
    def __init__(self, open: bool, code: Optional[int]):
        self.open = open
        self.code = code

    @classmethod
    def from_ansible(cls, ansible_data: Any) -> Any:
        pass

    @classmethod
    def from_hypercore(
        cls, hypercore_data: dict[str, Union[int, bool, None]]
    ) -> SupportTunnel:
        # There is no None check since get_record is not used (support_tunnel's api behaves different)
        if not hypercore_data["tunnelOpen"]:
            open = False
            code = None
        else:
            open = True
            code = hypercore_data["tunnelOpen"]
        return cls(open=open, code=code)

    def to_hypercore(self) -> Any:
        pass

    def to_ansible(self) -> TypedSupportTunnelToAnsible:
        return dict(
            open=self.open,
            code=self.code,
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
        return all(
            (
                self.open == other.open,
                self.code == other.code,
            )
        )

    @classmethod
    def check_tunnel_status(cls, client: Client) -> SupportTunnel:
        response = client.get("/support-api/check")  # type: ignore
        return cls.from_hypercore(response.json)

    @staticmethod
    def open_tunnel(module: AnsibleModule, client: Client) -> None:
        client.get(
            "/support-api/open", query={"code": module.params["code"]}
        )  # type: ignore

    @staticmethod
    def close_tunnel(client: Client) -> None:
        client.get("/support-api/close")  # type: ignore
