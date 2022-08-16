# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from unittest.mock import MagicMock
import os

from ansible_collections.scale_computing.hypercore.plugins.module_utils.client import (
    Client,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.rest_client import (
    RestClient,
)

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import (
    VM,
)

from ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag import (
    TaskTag,
)


@pytest.fixture
def client(mocker):
    return mocker.Mock(spec=Client)


@pytest.fixture
def rest_client(mocker):
    return mocker.Mock(spec=RestClient(client=client))


@pytest.fixture
def vm(mocker):
    # Fixture for object VM. Used in tests, where it isn't really relevant with what the VM is initialized with
    return mocker.Mock(spec=VM)


@pytest.fixture
def task_wait():
    task_tag = TaskTag
    task_tag.wait_task = MagicMock(return_value=None)
    return task_tag


@pytest.fixture
def create_module(mocker):
    # Fixture for creating AnsibleModule instance mocks. All instance mocks are limited
    # in what method calls they allow in order to enforce rules for writing ServiceNow
    # modules.

    def constructor(params=None, check_mode=False):
        return mocker.Mock(
            spec_set=["check_mode", "deprecate", "params", "warn", "sha256"],
            params=params or {},
            check_mode=check_mode,
        )

    return constructor


@pytest.fixture
def os_stat():
    os.stat = MagicMock(return_value=os.stat_result((0, 0, 0, 0, 0, 0, 0, 0, 0, 0)))


# Helpers for testing module invocation (parameter parsing and validation). Adapted from
# https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html and made
# into a reusable pytest fixture.


class AnsibleRunEnd(Exception):
    def __init__(self, success, result):
        super(AnsibleRunEnd, self).__init__("End task run")

        self.success = success
        self.result = result


def exit_json_mock(self, **result):
    raise AnsibleRunEnd(True, result)


def fail_json_mock(self, **result):
    raise AnsibleRunEnd(False, result)


def run_mock(module, client, another_client=None):
    return False, {}, dict(before={}, after={})


@pytest.fixture
def run_main(mocker):
    def runner(module, params=None):
        args = dict(
            ANSIBLE_MODULE_ARGS=dict(
                _ansible_remote_tmp="/tmp",
                _ansible_keep_remote_files=False,
            ),
        )
        args["ANSIBLE_MODULE_ARGS"].update(params or {})
        mocker.patch.object(basic, "_ANSIBLE_ARGS", to_bytes(json.dumps(args)))

        # We can mock the run function because we enforce module structure in our
        # development guidelines.
        mocker.patch.object(module, "run", run_mock)

        try:
            module.main()
        except AnsibleRunEnd as e:
            return e.success, e.result
        assert False, "Module is not calling exit_json or fail_json."

    mocker.patch.multiple(
        basic.AnsibleModule, exit_json=exit_json_mock, fail_json=fail_json_mock
    )
    return runner
