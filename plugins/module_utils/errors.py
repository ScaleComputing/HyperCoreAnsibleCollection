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


# In-case function parameter is optional but required
class MissingFunctionParameter(ScaleComputingError):
    def __init__(self, data):
        self.message = "Missing parameter - {0}".format(data)
        super(MissingFunctionParameter, self).__init__(self.message)


# In-case argument spec doesn't catch exception
class MissingValueAnsible(ScaleComputingError):
    def __init__(self, data):
        self.message = "Missing value - {0}".format(data)
        super(MissingValueAnsible, self).__init__(self.message)


# In-case argument spec doesn't catch exception
class MissingValueHC3(ScaleComputingError):
    def __init__(self, data):
        self.message = "Missing value - {0}".format(data)
        super(MissingValueHC3, self).__init__(self.message)


class DeviceNotUnique(ScaleComputingError):
    def __init__(self, data):
        self.message = "Device is not unique - {0}".format(data)
        super(DeviceNotUnique, self).__init__(self.message)


class VMNotFound(ScaleComputingError):
    def __init__(self, data):
        self.message = "Virtual machine - {0} - not found".format(data)
        super(VMNotFound, self).__init__(self.message)


class ReplicationNotUnique(ScaleComputingError):
    def __init__(self, data):
        self.message = "There is already a replication on - {0} - virtual machine".format(data)
        super(ReplicationNotUnique, self).__init__(self.message)

