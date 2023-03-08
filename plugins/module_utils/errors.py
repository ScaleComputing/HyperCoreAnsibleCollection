# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from typing import Union
from ansible.module_utils.urls import Request


class ScaleComputingError(Exception):
    pass


class AuthError(ScaleComputingError):
    pass


class UnexpectedAPIResponse(ScaleComputingError):
    def __init__(self, response: Request):
        self.message = "Unexpected response - {0} {1}".format(
            response.status, response.data
        )
        self.response_status = response.status
        super(UnexpectedAPIResponse, self).__init__(self.message)


class InvalidUuidFormatError(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "Invalid UUID - {0}".format(data)
        super(InvalidUuidFormatError, self).__init__(self.message)


# In-case function parameter is optional but required
class MissingFunctionParameter(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "Missing parameter - {0}".format(data)
        super(MissingFunctionParameter, self).__init__(self.message)


# In-case argument spec doesn't catch exception
class MissingValueAnsible(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "Missing value - {0}".format(data)
        super(MissingValueAnsible, self).__init__(self.message)


# In-case argument spec doesn't catch exception
class MissingValueHypercore(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "Missing values from hypercore API - {0}".format(data)
        super(MissingValueHypercore, self).__init__(self.message)


class DeviceNotUnique(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "Device is not unique - {0} - already exists".format(data)
        super(DeviceNotUnique, self).__init__(self.message)


class VMNotFound(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "Virtual machine - {0} - not found".format(data)
        super(VMNotFound, self).__init__(self.message)


class ReplicationNotUnique(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = (
            "There is already a replication on - {0} - virtual machine".format(data)
        )
        super(ReplicationNotUnique, self).__init__(self.message)


class ClusterConnectionNotFound(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "No cluster connection found - {0}".format(data)
        super(ClusterConnectionNotFound, self).__init__(self.message)


class SMBServerNotFound(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "SMB server is either not connected or not in the same network - {0}".format(
            data
        )
        super(SMBServerNotFound, self).__init__(self.message)


class VMInvalidParams(ScaleComputingError):
    def __init__(self) -> None:
        self.message = "Invalid set of parameters - strict affinity set to true and nodes not provided."
        super(VMInvalidParams, self).__init__(self.message)


class SupportTunnelError(ScaleComputingError):
    def __init__(self, data: Union[str, Exception]):
        self.message = "{0}".format(data)
        super(SupportTunnelError, self).__init__(self.message)
