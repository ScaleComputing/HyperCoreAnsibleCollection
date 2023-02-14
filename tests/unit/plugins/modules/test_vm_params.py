from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_params
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-unique-name",
            vm_name_new="VM-unique-name-updated",
            description="Updated parameters",
            tags=["Xlab"],
            memory=512,
            vcpu=2,
            power_state="start",
            snapshot_schedule="snapshot_schedule",
        )
        success, result = run_main(vm_params, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            vm_name="VM-name-unique",
        )
        success, result = run_main(vm_params, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(vm_params)

        assert success is False
        assert "missing required arguments: vm_name" in result["msg"]
