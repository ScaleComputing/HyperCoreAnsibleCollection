# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from typing import TypedDict, Union, Any

# Typed Classes use for Python hints.


# Registration to ansible return dict.
class TypedRegistrationToAnsible(TypedDict):
    company_name: Union[str, None]
    contact: Union[str, None]
    phone: Union[str, None]
    email: Union[str, None]


# Registration from ansible input dict.
class TypedRegistrationFromAnsible(TypedDict):
    company_name: Union[str, None]
    contact: Union[str, None]
    phone: Union[str, None]
    email: Union[str, None]


# Task tag return dict.
class TypedTaskTag(TypedDict):
    createdUUID: str
    taskTag: str


# DNSConfig to ansible return dict.
class TypedDNSConfigToAnsible(TypedDict):
    uuid: str
    name: str


# Support_tunnel to ansible return dict.
class TypedSupportTunnelToAnsible(TypedDict):
    open: bool
    code: Union[int, None]


# User to ansible return dict.
class TypedUserToAnsible(TypedDict):
    uuid: str
    username: str
    full_name: str
    roles: list[TypedRoleToAnsible]
    session_limit: int


# Role to ansible return dict.
class TypedRoleToAnsible(TypedDict):
    uuid: str
    name: str


# Cluster to ansible return dict.
class TypedClusterToAnsible(TypedDict):
    uuid: str
    name: str


# Ansible module return Diff dict {before:{} after:{}}
class TypedDiff(TypedDict):
    before: Union[
        TypedRegistrationToAnsible,
        TypedSupportTunnelToAnsible,
        TypedUserToAnsible,
        TypedClusterToAnsible,
        None,
    ]
    after: Union[
        TypedRegistrationToAnsible,
        TypedSupportTunnelToAnsible,
        TypedUserToAnsible,
        TypedClusterToAnsible,
        None,
    ]


# smtp module
class TypedSmtpToAnsible(TypedDict):
    uuid: Union[str, None]
    smtp_server: Union[str, None]
    port: Union[int, None]
    use_ssl: Union[bool, None]
    use_auth: Union[bool, None]
    auth_user: Union[str, None]
    auth_password: Union[str, None]
    from_address: Union[str, None]
    latest_task_tag: Union[TypedTaskTag, dict[Any, Any], None]


class TypedSmtpFromAnsible(TypedDict):
    uuid: Union[str, None]
    smtp_server: Union[str, None]
    port: Union[int, None]
    use_ssl: Union[bool, None]
    use_auth: Union[bool, None]
    auth_user: Union[str, None]
    auth_password: Union[str, None]
    from_address: Union[str, None]
    latest_task_tag: Union[TypedTaskTag, None]


class TypedEmailAlertToAnsible(TypedDict):
    uuid: Union[str, None]
    alert_tag_uuid: Union[str, None]
    email_address: Union[str, None]
    resend_delay: Union[int, None]
    silent_period: Union[int, None]
    latest_task_tag: Union[TypedTaskTag, dict[Any, Any], None]


class TypedEmailAlertFromAnsible(TypedDict):
    uuid: Union[str, None]
    alert_tag_uuid: Union[str, None]
    email_address: Union[str, None]
    resend_delay: Union[int, None]
    silent_period: Union[int, None]
    latest_task_tag: Union[TypedTaskTag, None]


class TypedVirtualDiskToAnsible(TypedDict):
    name: Union[str, None]
    uuid: Union[str, None]
    block_size: Union[int, None]
    size: Union[int, None]
    # allocated_size: int
    replication_factor: Union[int, None]


class TypedVirtualDiskFromAnsible(TypedDict):
    name: Union[str, None]
    # uuid: str
