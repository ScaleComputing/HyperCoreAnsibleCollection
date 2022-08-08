# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

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