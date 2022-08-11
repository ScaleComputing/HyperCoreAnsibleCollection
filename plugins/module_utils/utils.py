# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from abc import abstractmethod

__metaclass__ = type

import uuid

from ..module_utils.errors import InvalidUuidFormatError


def validate_uuid(value):
    try:
        uuid.UUID(value, version=4)
    except ValueError:
        raise InvalidUuidFormatError(value)


def filter_dict(input, *field_names):
    output = {}
    for field_name in field_names:
        value = input[field_name]
        if value is not None:
            output[field_name] = value
    return output


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
    def from_ansible(self, ansible_data):
        """
        Transforms from ansible_data (module.params) to python-object.
        :param ansible_data: Field that is inputed from ansible playbook. Is most likely
        equivalent to "module.params" in python
        :return: python object
        """
        pass

    @classmethod
    @abstractmethod
    def from_hypercore(self, hypercore_data):
        """
        Transforms from hypercore-native dictionary to python-object.
        :param hypercore_data: Dictionary from hypercore API
        :return: python object
        """
        pass
