from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    oidc_config_info,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc import (
    Oidc,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestMain:
    def test_minimal_set_of_params(self, run_main_info) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
        )

        success, results = run_main_info(oidc_config_info, params)
        assert success is True
        assert results == {"changed": False, "record": []}

    def test_maximum_set_of_params(self, run_main_info) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
        )

        success, results = run_main_info(oidc_config_info, params)
        assert success is True
        assert results == {"changed": False, "record": []}


class TestRun:
    def test_run_oidc_info_without_record(
        self, create_module, rest_client, mocker
    ) -> None:
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
            )
        )
        rest_client.list_records.return_value = []
        results = oidc_config_info.run(module, rest_client)
        assert isinstance(results, tuple)
        assert results == (False, None)

    def test_run_oidc_info_with_record(
        self, create_module, rest_client, mocker
    ) -> None:
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
            )
        )
        oidc_obj = Oidc(
            uuid="123",
            client_id="123",
            config_url="this_config",
            certificate="this_cert",
            scopes="this_scopes",
        )
        rest_client.list_records.return_value = [
            dict(
                uuid="123",
                client_id="123",
                config_url="this_config",
                scopes="this_scopes",
            )
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc.Oidc.from_hypercore"
        ).return_value = oidc_obj
        results = oidc_config_info.run(module, rest_client)
        assert isinstance(results, tuple)
        assert results == (
            False,
            dict(
                client_id="123",
                config_url="this_config",
                scopes="this_scopes",
            ),
        )
