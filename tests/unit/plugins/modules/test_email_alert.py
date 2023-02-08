# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert import (
    EmailAlert,
)
from ansible_collections.scale_computing.hypercore.plugins.modules import email_alert

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestModifyEmailAlert:
    pass


class TestMain:
    pass
