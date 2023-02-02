# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from typing import TypedDict, Union, Any


# Use for type hinting.
class TypedRegistrationToAnsible(TypedDict):
    company_name: Union[str, None]
    contact: Union[str, None]
    phone: Union[str, None]
    email: Union[str, None]


# Use for type hinting.
class TypedRegistrationFromAnsible(TypedDict):
    company_name: Union[str, None]
    contact: Union[str, None]
    phone: Union[str, None]
    email: Union[str, None]


# Use for type hinting.
class TypedTaskTag(TypedDict):
    createdUUID: str
    taskTag: str


# Use for type hinting.
class TypedDNSConfigToAnsible(TypedDict):
    uuid: str
    name: str


class TypedDiff(TypedDict):
    before: Union[dict[Any, Any], TypedRegistrationToAnsible, None]
    after: Union[dict[Any, Any], TypedRegistrationToAnsible, None]
