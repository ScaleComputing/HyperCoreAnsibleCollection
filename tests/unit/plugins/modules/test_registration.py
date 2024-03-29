from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import registration
from ansible_collections.scale_computing.hypercore.plugins.module_utils.registration import (
    Registration,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestMain:
    def test_minimal_set_of_params(self, run_main) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            state="present",
        )

        success, results = run_main(registration, params)

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
            state="present",
            company_name="this_company",
            contact="this_contact",
            email="this_email",
            phone="this_phone",
        )

        success, results = run_main(registration, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }


class TestRun:
    def test_run_with_present_registration(
        self, create_module, rest_client, mocker
    ) -> None:
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                state="present",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.get"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.registration.ensure_present"
        ).return_value = (True, {}, {})
        results = registration.run(module, rest_client)
        assert isinstance(results, tuple)
        assert results == (True, {}, {})

    def test_run_with_absent_registration(
        self, create_module, rest_client, mocker
    ) -> None:
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                state="absent",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.get"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.registration.ensure_absent"
        ).return_value = (True, {}, {})
        results = registration.run(module, rest_client)
        assert isinstance(results, tuple)
        assert results == (True, {}, {})


class TestEnsurePresent:
    def test_ensure_present_when_create_registration(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                state="present",
                company_name="new_name",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.send_create_request"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.get"
        ).return_value = {}
        result = registration.ensure_present(module, rest_client, None)
        assert isinstance(result, tuple)
        assert result == (False, None, {"before": None, "after": None})

    def test_ensure_present_when_update_registration(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                state="present",
                company_name="new_name",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.send_update_request"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.get"
        ).return_value = {}
        mocker_registration = Registration()
        result = registration.ensure_present(module, rest_client, mocker_registration)
        assert isinstance(result, tuple)
        assert result == (
            True,
            None,
            {
                "before": {
                    "company_name": None,
                    "contact": None,
                    "phone": None,
                    "email": None,
                },
                "after": None,
            },
        )


class TestEnsureAbsent:
    def test_ensure_absent_when_exist_registration(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                state="absent",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.send_delete_request"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.get"
        ).return_value = {}
        mocker_registration = Registration()
        result = registration.ensure_absent(module, rest_client, mocker_registration)
        assert isinstance(result, tuple)
        assert result == (
            True,
            None,
            {
                "before": {
                    "company_name": None,
                    "contact": None,
                    "phone": None,
                    "email": None,
                },
                "after": None,
            },
        )

    def test_ensure_absent_when_not_exist_registration(
        self, create_module, rest_client, mocker
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                state="absent",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.send_delete_request"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.registration.Registration.get"
        ).return_value = {}
        result = registration.ensure_absent(module, rest_client, None)
        assert isinstance(result, tuple)
        assert result == (False, None, {"before": None, "after": None})
