# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from .rest_client import RestClient

# from .client import Client
from ..module_utils.utils import PayloadMapper, get_query

from ..module_utils.typed_classes import (
    TypedTaskTag,
    TypedEmailAlertToAnsible,
    TypedEmailAlertFromAnsible,
)
from typing import Union, Any, Dict


class EmailAlert(PayloadMapper):
    def __init__(
        self,
        uuid: Union[str, None] = None,
        alert_tag_uuid: Union[str, None] = None,
        email_address: Union[str, None] = None,
        resend_delay: Union[int, None] = None,
        silent_period: Union[int, None] = None,
        latest_task_tag: Union[TypedTaskTag, dict[Any, Any], None] = None,
    ):
        self.uuid = uuid
        self.alert_tag_uuid = alert_tag_uuid
        self.email_address = email_address
        self.resend_delay = resend_delay
        self.silent_period = silent_period
        self.latest_task_tag = latest_task_tag if latest_task_tag is not None else {}

    @classmethod
    def from_ansible(cls, ansible_data: TypedEmailAlertFromAnsible):
        return EmailAlert(
            uuid=ansible_data["uuid"],
            alert_tag_uuid=ansible_data["alert_tag_uuid"],
            email_address=ansible_data["email_address"],
            resend_delay=ansible_data["resend_delay"],
            silent_period=ansible_data["silent_period"],
            latest_task_tag=ansible_data["latest_task_tag"],
        )

    @classmethod
    def from_hypercore(cls, hypercore_data: dict[Any, Any]):
        if not hypercore_data:
            return None
        return cls(
            uuid=hypercore_data["uuid"],
            alert_tag_uuid=hypercore_data["alertTagUUID"],
            email_address=hypercore_data["emailAddress"],
            resend_delay=hypercore_data["resendDelay"],
            silent_period=hypercore_data["silentPeriod"],
            latest_task_tag=hypercore_data["latestTaskTag"],
        )

    def to_hypercore(self) -> dict[Any, Any]:
        return dict(
            alertTagUUID=self.alert_tag_uuid,
            emailAddress=self.email_address,
            resendDelay=self.resend_delay,
            silentPeriod=self.silent_period,
        )

    def to_ansible(self) -> TypedEmailAlertToAnsible:
        return dict(
            uuid=self.uuid,
            alert_tag_uuid=self.alert_tag_uuid,
            email_address=self.email_address,
            resend_delay=self.resend_delay,
            silent_period=self.silent_period,
            latest_task_tag=self.latest_task_tag,
        )

    # This method is here for testing purposes!
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EmailAlert):
            return NotImplemented
        return all(
            (
                self.uuid == other.uuid,
                self.alert_tag_uuid == other.alert_tag_uuid,
                self.email_address == other.email_address,
                self.resend_delay == other.resend_delay,
                self.silent_period == other.silent_period,
                self.latest_task_tag == other.latest_task_tag,
            )
        )

    @classmethod
    def get_by_uuid(
        cls,
        ansible_dict: Dict[Any, Any],
        rest_client: RestClient,
        must_exist: bool = False,
    ):
        query = get_query(ansible_dict, "uuid", ansible_hypercore_map=dict(uuid="uuid"))
        hypercore_dict = rest_client.get_record(
            "/rest/v1/AlertEmailTarget", query, must_exist=must_exist
        )
        alert_email_from_hypercore = cls.from_hypercore(hypercore_dict)
        return alert_email_from_hypercore

    @classmethod
    def get_by_email(
        cls,
        ansible_dict: Dict[Any, Any],
        rest_client: RestClient,
        must_exist: bool = False,
    ):
        query = get_query(
            ansible_dict,
            "email_address",
            ansible_hypercore_map=dict(email_address="emailAddress"),
        )
        hypercore_dict = rest_client.get_record(
            "/rest/v1/AlertEmailTarget", query, must_exist=must_exist
        )

        alert_email_from_hypercore = EmailAlert.from_hypercore(hypercore_dict)
        return alert_email_from_hypercore

    @classmethod
    def get_state(
        cls,
        rest_client: RestClient,
    ):
        state = [
            EmailAlert.from_hypercore(hypercore_data=hypercore_dict).to_ansible()
            for hypercore_dict in rest_client.list_records("/rest/v1/AlertEmailTarget/")
        ]

        return state

    @classmethod
    def create(
        cls,
        rest_client: RestClient,
        payload: Dict[Any, Any],
        check_mode: bool = False,
    ) -> None:
        rest_client.create_record("/rest/v1/AlertEmailTarget/", payload, check_mode)

    def update(
        self,
        rest_client: RestClient,
        payload: Dict[Any, Any],
        check_mode: bool = False,
    ) -> None:
        rest_client.update_record(
            f"/rest/v1/AlertEmailTarget/{self.uuid}", payload, check_mode
        )

    def delete(
        self,
        rest_client: RestClient,
        check_mode: bool = False,
    ) -> None:
        rest_client.delete_record(f"/rest/v1/AlertEmailTarget/{self.uuid}", check_mode)

    def test(
        self,
        rest_client: RestClient,
    ) -> TypedTaskTag:
        response = rest_client.client.post(
            f"/rest/v1/AlertEmailTarget/{self.uuid}/test", None
        )
        return response
