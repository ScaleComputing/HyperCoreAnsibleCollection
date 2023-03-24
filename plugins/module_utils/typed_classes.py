# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from typing import TypedDict, Union, Any, Optional


# Typed Classes use for Python hints.


class TypedClusterInstance(TypedDict):
    host: str
    username: str
    password: str
    timeout: float


# Registration to ansible return dict.
class TypedRegistrationToAnsible(TypedDict):
    company_name: Optional[str]
    contact: Optional[str]
    phone: Optional[str]
    email: Optional[str]


# Registration from ansible input dict.
class TypedRegistrationFromAnsible(TypedDict):
    company_name: Optional[str]
    contact: Optional[str]
    phone: Optional[str]
    email: Optional[str]


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
    code: Optional[int]


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


# OIDC to ansible return dict.
class TypedOidcToAnsible(TypedDict):
    client_id: Optional[str]
    config_url: Optional[str]
    scopes: Optional[str]


# OIDC from ansible dict.
class TypedOidcFromAnsible(TypedDict):
    client_id: str
    config_url: str
    scopes: str
    certificate: str
    shared_secret: str


# Cluster to ansible return dict.
class TypedClusterToAnsible(TypedDict):
    uuid: str
    name: str
    icos_version: str


class TypedCertificateToAnsible(TypedDict):
    certificate: str


# Update to ansible return dict.
class TypedUpdateToAnsible(TypedDict):
    uuid: str
    description: str
    change_log: str
    build_id: int
    major_version: int
    minor_version: int
    revision: int
    timestamp: int


# UpdateStatus to ansible return dict.
class TypedUpdateStatusToAnsible(TypedDict):
    prepare_status: str
    update_status: str
    from_build: str
    to_build: str
    to_version: str
    percent: str
    update_status_details: str
    usernotes: str


# Ansible module return Diff dict {before:{} after:{}}
class TypedDiff(TypedDict):
    before: Union[
        TypedRegistrationToAnsible,
        TypedSupportTunnelToAnsible,
        TypedUserToAnsible,
        TypedOidcToAnsible,
        TypedClusterToAnsible,
        TypedCertificateToAnsible,
        TypedSyslogServerToAnsible,
        TypedUpdateToAnsible,
        TypedVirtualDiskToAnsible,
        None,
        dict[None, None],
    ]
    after: Union[
        TypedRegistrationToAnsible,
        TypedSupportTunnelToAnsible,
        TypedUserToAnsible,
        TypedOidcToAnsible,
        TypedClusterToAnsible,
        TypedCertificateToAnsible,
        TypedSyslogServerToAnsible,
        TypedVirtualDiskToAnsible,
        None,
        dict[None, None],
    ]


# smtp module
class TypedSmtpToAnsible(TypedDict):
    uuid: Optional[str]
    server: Optional[str]
    port: Optional[int]
    use_ssl: Optional[bool]
    use_auth: Optional[bool]
    auth_user: Optional[str]
    auth_password: Optional[str]
    from_address: Optional[str]
    latest_task_tag: Union[TypedTaskTag, dict[Any, Any], None]


class TypedSmtpFromAnsible(TypedDict):
    uuid: Optional[str]
    server: Optional[str]
    port: Optional[int]
    use_ssl: Optional[bool]
    use_auth: Optional[bool]
    auth_user: Optional[str]
    auth_password: Optional[str]
    from_address: Optional[str]
    latest_task_tag: Optional[TypedTaskTag]


class TypedEmailAlertToAnsible(TypedDict):
    uuid: Optional[str]
    alert_tag_uuid: Optional[str]
    email: Optional[str]
    resend_delay: Optional[int]
    silent_period: Optional[int]
    latest_task_tag: Union[TypedTaskTag, dict[Any, Any], None]


class TypedEmailAlertFromAnsible(TypedDict):
    uuid: Optional[str]
    alert_tag_uuid: Optional[str]
    email: Optional[str]
    resend_delay: Optional[int]
    silent_period: Optional[int]
    latest_task_tag: Union[TypedTaskTag, None]


class TypedVirtualDiskToAnsible(TypedDict):
    name: Optional[str]
    uuid: Optional[str]
    block_size: Optional[int]
    size: Optional[int]
    # allocated_size: int
    replication_factor: Optional[int]


class TypedVirtualDiskFromAnsible(TypedDict):
    name: Optional[str]
    # uuid: str


class TypedSyslogServerToAnsible(TypedDict):
    uuid: Optional[str]
    alert_tag_uuid: Optional[str]
    host: Optional[str]
    port: Optional[int]
    protocol: Optional[str]
    resend_delay: Optional[int]
    silent_period: Optional[int]
    latest_task_tag: Union[TypedTaskTag, dict[Any, Any], None]


class TypedSyslogServerFromAnsible(TypedDict):
    uuid: Optional[str]
    host: Optional[str]
    port: Optional[int]
    protocol: Optional[str]


class TypedVMSnapshotToAnsible(TypedDict):
    snapshot_uuid: Optional[str]
    vm: Optional[dict[Any, Any]]
    label: Optional[str]
    type: Optional[str]
    timestamp: Optional[int]
    automated_trigger_timestamp: Optional[int]
    local_retain_until_timestamp: Optional[int]
    remote_retain_until_timestamp: Optional[int]
    block_count_diff_from_serial_number: Optional[int]
    replication: Optional[bool]


class TypedVMSnapshotFromAnsible(TypedDict):
    snapshot_uuid: Optional[str]
    vm: Optional[dict[Any, Any]]
    snapshot_serial_number: Optional[int]
    label: Optional[str]
    type: Optional[str]
