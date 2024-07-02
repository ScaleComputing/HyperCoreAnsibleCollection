# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from .rest_client import RestClient

from ..module_utils.utils import PayloadMapper, get_query
from ..module_utils.task_tag import TaskTag

from ..module_utils.typed_classes import (
    TypedTaskTag,
    TypedSyslogServerToAnsible,
    TypedSyslogServerFromAnsible,
)
from typing import List, Union, Any, Dict, Optional

protocols = {"SYSLOG_PROTOCOL_TCP": "tcp", "SYSLOG_PROTOCOL_UDP": "udp"}


class SyslogServer(PayloadMapper):
    def __init__(
        self,
        uuid: Optional[str] = None,
        alert_tag_uuid: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        protocol: Optional[str] = None,
        resend_delay: Optional[int] = None,
        silent_period: Optional[int] = None,
        latest_task_tag: Union[TypedTaskTag, dict[Any, Any], None] = None,
    ):
        self.uuid = uuid
        self.alert_tag_uuid = alert_tag_uuid
        self.host = host
        self.port = port
        self.protocol = protocol
        self.resend_delay = resend_delay
        self.silent_period = silent_period
        self.latest_task_tag = latest_task_tag if latest_task_tag is not None else {}

    @classmethod
    def from_ansible(cls, ansible_data: TypedSyslogServerFromAnsible) -> SyslogServer:
        return SyslogServer(
            uuid=ansible_data.get("uuid"),
            host=ansible_data["host"],
            port=ansible_data["port"],
            protocol=ansible_data["protocol"],
        )

    @classmethod
    def from_hypercore(cls, hypercore_data: Dict[Any, Any]) -> SyslogServer:
        if not hypercore_data:
            raise AssertionError("hypercore_data dict must be non-emtpy")
        return cls(
            uuid=hypercore_data["uuid"],
            alert_tag_uuid=hypercore_data["alertTagUUID"],
            host=hypercore_data["host"],
            port=hypercore_data["port"],
            protocol=protocols[hypercore_data["protocol"]],
            resend_delay=hypercore_data["resendDelay"],
            silent_period=hypercore_data["silentPeriod"],
            latest_task_tag=hypercore_data["latestTaskTag"],
        )

    def to_hypercore(self) -> Dict[Any, Any]:
        return dict(
            host=self.host,
            port=self.port,
            protocol=self.protocol,
        )

    def to_ansible(self) -> TypedSyslogServerToAnsible:
        return dict(
            uuid=self.uuid,
            alert_tag_uuid=self.alert_tag_uuid,
            host=self.host,
            port=self.port,
            protocol=self.protocol,
            resend_delay=self.resend_delay,
            silent_period=self.silent_period,
            latest_task_tag=self.latest_task_tag,
        )

    # This method is here for testing purposes!
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SyslogServer):
            return NotImplemented
        return all(
            (
                self.uuid == other.uuid,
                self.alert_tag_uuid == other.alert_tag_uuid,
                self.host == other.host,
                self.port == other.port,
                self.protocol == other.protocol,
                self.resend_delay == other.resend_delay,
                self.silent_period == other.silent_period,
                self.latest_task_tag == other.latest_task_tag,
            )
        )

    def is_equivalent(self, other: SyslogServer) -> bool:
        """
        Method compares if two objects are "equal".
        Equal in sense are equal all attributes configurable via GUI and/or ansible module.

        This is not __eq__ method, as __eq__ is already used "for CI testing purposes only",
        in this and most other classes.
        """
        if self.host != other.host:
            return False
        if self.port != other.port:
            return False
        if self.protocol != other.protocol:
            return False
        return True

    @classmethod
    def get_by_uuid(
        cls,
        ansible_dict: Dict[Any, Any],
        rest_client: RestClient,
        must_exist: bool = False,
    ) -> Optional[SyslogServer]:
        query = get_query(ansible_dict, "uuid", ansible_hypercore_map=dict(uuid="uuid"))
        hypercore_dict = rest_client.get_record(
            "/rest/v1/AlertSyslogTarget", query, must_exist=must_exist
        )
        if hypercore_dict is None:
            return None
        syslog_server_from_hypercore = cls.from_hypercore(hypercore_dict)
        return syslog_server_from_hypercore

    @classmethod
    def get_by_host(
        cls,
        host: str,
        rest_client: RestClient,
        must_exist: bool = False,
    ) -> Optional[SyslogServer]:
        hypercore_dict = rest_client.get_record(
            "/rest/v1/AlertSyslogTarget", {"host": host}, must_exist=must_exist
        )
        if hypercore_dict is None:
            return None

        syslog_server = SyslogServer.from_hypercore(hypercore_dict)
        return syslog_server

    def __lt__(self, other: SyslogServer) -> bool:
        # API response is sorted by UUID.
        # We want to sort by host, port, protocol.
        if self.host is None:
            raise AssertionError()
        if self.port is None:
            raise AssertionError()
        if self.protocol is None:
            raise AssertionError()
        if other.host is None:
            raise AssertionError()
        if other.port is None:
            raise AssertionError()
        if other.protocol is None:
            raise AssertionError()

        if self.host < other.host:
            return True
        elif self.host > other.host:
            return False
        if self.port < other.port:
            return True
        elif self.port > other.port:
            return False
        if self.protocol < other.protocol:
            return True
        elif self.protocol > other.protocol:
            return False
        return False

    @classmethod
    def get_all(
        cls,
        rest_client: RestClient,
    ) -> List[SyslogServer]:
        syslog_servers = [
            cls.from_hypercore(hypercore_data=hypercore_dict)
            for hypercore_dict in rest_client.list_records(
                "/rest/v1/AlertSyslogTarget/"
            )
        ]
        syslog_servers.sort()
        return syslog_servers

    @classmethod
    def get_state(
        cls,
        rest_client: RestClient,
    ) -> List[TypedSyslogServerToAnsible]:
        syslog_servers = cls.get_all(rest_client)
        state = [ss.to_ansible() for ss in syslog_servers]
        return state

    @classmethod
    def create(
        cls,
        rest_client: RestClient,
        payload: Dict[Any, Any],
        check_mode: bool = False,
    ) -> SyslogServer:
        task_tag = rest_client.create_record(
            "/rest/v1/AlertSyslogTarget/", payload, check_mode
        )
        TaskTag.wait_task(rest_client, task_tag)
        syslog_server = cls.get_by_uuid(
            dict(uuid=task_tag["createdUUID"]),
            rest_client,
            must_exist=True,
        )
        if syslog_server is None:
            raise AssertionError()
        return syslog_server

    def update(
        self,
        rest_client: RestClient,
        payload: Dict[Any, Any],
        check_mode: bool = False,
    ) -> None:
        task_tag = rest_client.update_record(
            f"/rest/v1/AlertSyslogTarget/{self.uuid}", payload, check_mode
        )
        TaskTag.wait_task(rest_client, task_tag)

    def delete(
        self,
        rest_client: RestClient,
        check_mode: bool = False,
    ) -> None:
        task_tag = rest_client.delete_record(
            f"/rest/v1/AlertSyslogTarget/{self.uuid}", check_mode
        )
        TaskTag.wait_task(rest_client, task_tag)
