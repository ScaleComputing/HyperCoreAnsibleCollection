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
