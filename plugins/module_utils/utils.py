# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations
from abc import abstractmethod

__metaclass__ = type

import uuid

from ..module_utils.errors import InvalidUuidFormatError
from typing import Union, Any
from ..module_utils.typed_classes import (
    TypedTaskTag,
    TypedRegistrationToAnsible,
    TypedOidcToAnsible,
    TypedCertificateToAnsible,
)


MIN_PYTHON_VERSION = (3, 8)


# Used in case of check mode
MOCKED_TASK_TAG = TypedTaskTag(
    createdUUID="0000000000",
    taskTag="00000",
)


def validate_uuid(value):
    try:
        uuid.UUID(value, version=4)
    except ValueError:
        raise InvalidUuidFormatError(value)


def get_query(
    input: dict[Any, Any], *field_names: str, ansible_hypercore_map: dict[Any, Any]
):
    """
    Wrapps filter_dict and transform_ansible_to_hypercore_query. Prefer to use 'get_query' over filter_dict
    even if there's no mapping between hypercore and ansible columns for the sake of verbosity and consistency
    """
    ansible_query = filter_dict(input, *field_names)
    hypercore_query = transform_query(ansible_query, ansible_hypercore_map)
    return hypercore_query


def filter_dict(input, *field_names):
    output = {}
    for field_name in field_names:
        if field_name not in input:
            continue
        value = input[field_name]
        if value is not None:
            output[field_name] = value
    return output


def transform_query(raw_query, query_map):
    # Transforms query by renaming raw_query's keys by specifying those keys and the new values in query_map
    return {query_map[key]: raw_query[key] for key, value in raw_query.items()}


class PayloadMapper:

    """
    Represent abstract class from which each 'endpoint class' will inherit from.
    Every class that will represent module object will (most likely) have to implement those methods.
    """

    @abstractmethod
    def to_ansible(self):
        """
        Transforms from python-native to ansible-native object.
        Used mostly in *_info modules for performing GET requests
        :return: ansible-native dictionary.
        """
        pass

    @abstractmethod
    def to_hypercore(self):
        """
        Transforms python-native to hypercore-native object.
        Used for using either post or patch methods onto hypercore API.
        :return: hypercore-native dictionary.
        """
        pass

    @classmethod
    @abstractmethod
    def from_ansible(cls, ansible_data):
        """
        Transforms from ansible_data (module.params) to python-object.
        :param ansible_data: Field that is inputed from ansible playbook. Is most likely
        equivalent to "module.params" in python
        :return: python object
        """
        pass

    @classmethod
    @abstractmethod
    def from_hypercore(cls, hypercore_data):
        """
        Transforms from hypercore-native dictionary to python-object.
        :param hypercore_data: Dictionary from hypercore API
        :return: python object
        """
        pass

    def __str__(self):
        return str(dict(ansible=self.to_ansible(), hypercore=self.to_hypercore()))


def is_superset(superset, candidate):
    if not candidate:
        return True
    for k, v in candidate.items():
        if k in superset and superset[k] == v:
            continue
        return False
    return True


def filter_results(results, filter_data) -> list[Any]:
    return [element for element in results if is_superset(element, filter_data)]


def is_changed(
    before: Union[
        TypedCertificateToAnsible, TypedOidcToAnsible, TypedRegistrationToAnsible, None
    ],
    after: Union[
        TypedCertificateToAnsible, TypedOidcToAnsible, TypedRegistrationToAnsible, None
    ],
) -> bool:
    return not before == after
