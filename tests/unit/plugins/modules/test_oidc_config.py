from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import oidc_config
from ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc import (
    Oidc,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_minimal_set_of_params(self, run_main) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            client_id="this_client",
            scopes="this_scopes",
            shared_secret="this_shared_secret",
            config_url="this_config_url",
        )

        success, results = run_main(oidc_config, params)

        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_maximum_set_of_params(self, run_main) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            client_id="this_client",
            scopes="this_scopes",
            shared_secret="this_shared_secret",
            config_url="this_config_url",
            certificate="this_certificate",
        )

        success, results = run_main(oidc_config, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }


class TestRun:
    def test_run_with_present_oidc(self, create_module, rest_client, mocker) -> None:
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                client_id="this_client",
                scopes="this_scopes",
                shared_secret="this_shared_secret",
                config_url="this_config_url",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc.Oidc.get"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.oidc_config.ensure_present"
        ).return_value = (True, {}, {})
        results = oidc_config.run(module, rest_client)
        assert isinstance(results, tuple)
        assert results == (True, {}, {})


class TestEnsurePresent:
    def test_ensure_present_when_create_oidc(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                client_id="this_client",
                scopes="this_scopes",
                shared_secret="this_shared_secret",
                config_url="this_config_url",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc.Oidc.send_create_request"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc.Oidc.get"
        ).return_value = {}
        result = oidc_config.ensure_present(module, rest_client, None)
        assert isinstance(result, tuple)
        assert result == (False, None, {"before": None, "after": None})

    def test_ensure_present_when_update_oidc(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                client_id="this_client",
                scopes="this_scopes",
                shared_secret="this_shared_secret",
                config_url="this_config_url",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc.Oidc.send_update_request"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.oidc.Oidc.get"
        ).return_value = {}
        mocker_registration = Oidc()
        result = oidc_config.ensure_present(module, rest_client, mocker_registration)
        assert isinstance(result, tuple)
        assert result == (
            True,
            None,
            {
                "before": {
                    "client_id": None,
                    "scopes": None,
                    "certificate": None,
                    "config_url": None,
                },
                "after": None,
            },
        )
