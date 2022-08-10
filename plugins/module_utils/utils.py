# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from abc import ABC, abstractmethod

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
    def to_ansible(self, hypercore_data):
        pass

    @abstractmethod
    def to_hypercore(self, ansible_data):
        pass

    @abstractmethod
    def from_ansible(self, hypercore_data):
        pass

    @abstractmethod
    def from_hypercore(self, ansible_data):
        pass
