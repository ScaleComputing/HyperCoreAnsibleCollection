# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import certificate
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestMain:
    def test_params_certificate(self, run_main) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            private_key="this_key",
            certificate="this_certificate",
        )

        success, results = run_main(certificate, params)

        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }


class TestRun:
    def test_run_with_present_certificate(
        self, create_module, rest_client, mocker
    ) -> None:
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                private_key="this_key",
                certificate="this_certificate",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.certificate.ensure_present"
        ).return_value = (True, {}, {}, False)
        results = certificate.run(module, rest_client)
        assert isinstance(results, tuple)
        assert results == (True, {}, {}, False)


class TestPresent:
    def test_present_certificate(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                private_key="this_key",
                certificate="this_certificate",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.certificate.get_certificate"
        ).side_effect = ["not_this_certificate", "this_certificate"]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.certificate.upload_cert"
        ).return_value = dict(taskTag="123", uuid="123")
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = None
        results = certificate.ensure_present(module, rest_client)
        assert results == (
            True,
            {"certificate": "this_certificate"},
            {
                "before": {"certificate": "not_this_certificate"},
                "after": {"certificate": "this_certificate"},
            },
        )


class TestUtils:
    def test_get_certificate_when_exist(self, create_module, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                private_key="this_key",
                certificate="this_certificate",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.certificate.ssl.get_server_certificate"
        ).return_value = "this_cert"
        results = certificate.get_certificate(module)
        assert isinstance(results, str)
        assert results == "this_cert"

    def test_get_certificate_when_not_exist(self, create_module, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                private_key="this_key",
                certificate="this_certificate",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.certificate.ssl.get_server_certificate"
        ).return_value = ""
        results = certificate.get_certificate(module)
        assert isinstance(results, str)
        assert results == ""

    def test_upload_certificate(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                private_key="this_key",
                certificate="this_certificate",
            )
        )
        rest_client.create_record.return_value = dict(createdUUID=123, taskTag=123)
        results = certificate.upload_cert(module, rest_client)
        assert isinstance(results, dict)
        assert results == dict(createdUUID=123, taskTag=123)
