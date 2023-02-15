# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
from ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert import EmailAlert
from ansible_collections.scale_computing.hypercore.plugins.modules import email_alert

from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestModifyEmailAlert:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )

    def test_create_email_alert(self, create_module, rest_client, task_wait, mocker):
        module = create_module(
            params=dict(
                cluster_instance=self.cluster_instance,
                email_alert="test@test.com",
                state="present",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.email_alert.EmailAlert.get_state"
        )
        rest_client.create_record.return_value = {
            "taskTag": 123,
        }


class TestMain:
    pass
