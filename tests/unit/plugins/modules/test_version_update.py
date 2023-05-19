from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import version_update
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestMain:
    def test_all_params(self, run_main, mocker):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="myuser",
                password="mypass",
            ),
            icos_version="9.2.11.210763",
        )

        success, result = run_main(version_update, params)

        assert success is True

    def test_required(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="myuser",
                password="mypass",
            ),
        )

        success, result = run_main(version_update, params)

        assert success is False
        assert "missing required arguments: icos_version" in result["msg"]
