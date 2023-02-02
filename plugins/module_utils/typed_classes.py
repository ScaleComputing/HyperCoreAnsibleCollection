# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

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

# Ansible module return Diff dict {before:{} after:{}}
class TypedDiff(TypedDict):
    before: Union[dict[Any, Any], TypedRegistrationToAnsible, None]
    after: Union[dict[Any, Any], TypedRegistrationToAnsible, None]
