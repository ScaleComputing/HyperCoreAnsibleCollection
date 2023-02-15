from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import cluster_name

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 8), reason="requires python3.8 or higher"
)


class TestMain:
    def test_all_params(self, run_main, mocker):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username=None,
                password=None,
            ),
            name_new="updated_name",
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.cluster_name.HyperCoreVersion"
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.cluster_name.HyperCoreVersion.verify"
        )

        success, result = run_main(cluster_name, params)

        assert success is True

    def test_required(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username=None,
                password=None,
            ),
        )

        success, result = run_main(cluster_name, params)

        assert success is False
        assert "missing required arguments: name_new" in result["msg"]
