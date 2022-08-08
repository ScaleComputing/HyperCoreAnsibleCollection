# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ScaleComputingError(Exception):
    pass


class AuthError(ScaleComputingError):
    pass


class UnexpectedAPIResponse(ScaleComputingError):
    def __init__(self, response):
        self.message = "Unexpected response - {0} {1}".format(
            response.status, response.data
        )
        super(UnexpectedAPIResponse, self).__init__(self.message)


class InvalidUuidFormatError(ScaleComputingError):
    def __init__(self, data):
        self.message = "Invalid UUID - {0}".format(data)
        super(InvalidUuidFormatError, self).__init__(self.message)


class MissingParameter(ScaleComputingError):
    def __init__(self, data):
        self.message = "Missing parameter - {0}".format(data)
        super(MissingParameter, self).__init__(self.message)


class MissingValue(ScaleComputingError):
    def __init__(self, data):
        self.message = "Missing value - {0}".format(data)
        super(MissingValue, self).__init__(self.message)


class DeviceNotUnique(ScaleComputingError):
    def __init__(self, data):
        self.message = "Device is not unique - {0}".format(data)
        super(DeviceNotUnique, self).__init__(self.message)
