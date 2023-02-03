# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper, get_query
from ..module_utils import errors


class SMTP(PayloadMapper):
    def __init__(
        self,
        uuid: str = None,
        smtp_server: str = None,
        port: int = None,
        use_ssl: bool = False,
        use_auth: bool = False,
        auth_user: str = None,
        auth_password: str = None,
        from_address: str = None,
        latest_task_tag: {} = None,
    ):
        self.uuid = uuid
        self.smtp_server = smtp_server
        self.port = port
        self.use_ssl = use_ssl
        self.use_auth = use_auth
        self.auth_user = auth_user
        self.auth_password = auth_password
        self.from_address = from_address
        self.latest_task_tag = latest_task_tag if latest_task_tag is not None else {}

    @classmethod
    def from_ansible(cls, ansible_data):
        return SMTP(
            uuid=ansible_data["uuid"],
            smtp_server=ansible_data["smtpServer"],
            port=ansible_data["port"],
            use_ssl=ansible_data["useSSL"],
            use_auth=ansible_data["useAuth"],
            auth_user=ansible_data["authUser"],
            auth_password=ansible_data["authPassword"],
            from_address=ansible_data["fromAddress"],
            latest_task_tag=ansible_data["latestTaskTag"],
        )

    @classmethod
    def from_hypercore(cls, hypercore_data):
        if not hypercore_data:
            return None

        return cls(
            uuid=hypercore_data["uuid"],
            smtp_server=hypercore_data["smtpServer"],
            port=hypercore_data["port"],
            use_ssl=hypercore_data["useSSL"],
            use_auth=hypercore_data["useAuth"],
            auth_user=hypercore_data["authUser"],
            auth_password=hypercore_data["authPassword"],
            from_address=hypercore_data["fromAddress"],
            latest_task_tag=hypercore_data["latestTaskTag"],
        )

    def to_hypercore(self):
        return dict(
            smtpServer=self.smtp_server,
            port=self.port,
            useSSL=self.use_ssl,
            useAuth=self.use_auth,
            authUser=self.auth_user,
            authPassword=self.auth_password,
            fromAddress=self.from_address,
        )

    def to_ansible(self):
        return dict(
            uuid=self.uuid,
            smtp_server=self.smtp_server,
            port=self.port,
            use_ssl=self.use_ssl,
            use_auth=self.use_auth,
            auth_user=self.auth_user,
            auth_password=self.auth_password,
            from_address=self.from_address,
            latest_task_tag=self.latest_task_tag,
        )

    # This method is here for testing purposes!
    def __eq__(self, other):
        return all(
            (
                self.uuid == other.uuid,
                self.smtp_server == other.smtp_server,
                self.port == other.port,
                self.use_ssl == other.use_ssl,
                self.use_auth == other.use_auth,
                self.auth_user == other.auth_user,
                self.auth_password == other.auth_password,
                self.from_address == other.from_address,
                self.latest_task_tag == other.latest_task_tag,
            )
        )

    @classmethod
    def get_by_uuid(cls, ansible_dict, rest_client, must_exist=False):
        query = get_query(ansible_dict, "uuid", ansible_hypercore_map=dict(uuid="uuid"))
        hypercore_dict = rest_client.get_record(
            "/rest/v1/AlertSMTPConfig", query, must_exist=must_exist
        )
        smtp_config_from_hypercore = SMTP.from_hypercore(hypercore_dict)
        return smtp_config_from_hypercore

    # This method is being tested with integration tests (dns_config_info)
    @classmethod
    def get_state(cls, rest_client):
        state = [
            SMTP.from_hypercore(hypercore_data=hypercore_dict).to_ansible()
            for hypercore_dict in rest_client.list_records("/rest/v1/AlertSMTPConfig/")
        ]

        # Raise an error if there is more than 1 DNS configuration available
        # - There should be 0 or 1 DNS configuration available
        if len(state) > 1:
            raise errors.ScaleComputingError(
                "SMTP Config: There are too many SMTP configuration settings!\n\
                The number of SMTP settings should be 0 or 1."
            )
        if len(state) == 0:
            return {}
        state[0].pop("auth_password")
        return state[0]
