from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import support_tunnel

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username=None,
                password=None,
            ),
            state="present",
            code=4422,
        )
        success, result = run_main(support_tunnel, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username=None,
                password=None,
            ),
            state="absent",
        )
        success, result = run_main(support_tunnel, params)

        assert success is True

    def test_required_if(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username=None,
                password=None,
            ),
            state="present",
        )
        success, result = run_main(support_tunnel, params)

        assert success is False
        assert (
            "state is present but all of the following are missing: code"
            in result["msg"]
        )

    def test_fail(self, run_main):
        success, result = run_main(support_tunnel)

        assert success is False
        assert "missing required arguments: state" in result["msg"]
