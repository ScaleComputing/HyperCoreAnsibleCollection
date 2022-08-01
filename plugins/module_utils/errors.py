# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ScaleComputingError(Exception):
    pass


class AuthError(ScaleComputingError):
    pass


class UnexpectedAPIResponse(ScaleComputingError):
    def __init__(self, status, data):
        self.message = "Unexpected response - {0} {1}".format(status, data)
        super(UnexpectedAPIResponse, self).__init__(self.message)
