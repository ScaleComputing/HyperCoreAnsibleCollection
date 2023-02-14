from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.user import User
from ansible_collections.scale_computing.hypercore.plugins.modules import user
from ansible_collections.scale_computing.hypercore.plugins.module_utils.role import Role
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestGetRoleUuids:
    def test_get_role_uuids(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                status="present",
                username="username",
                password="password",
                full_name="fullname",
                roles=["VM delete", "VM Create/Edit", "VM Power Controls"],
                session_limit=2,
            ),
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.user.Role.get_role_from_name"
        ).side_effect = [
            Role(
                uuid="9524382c-a199-47cc-bc94-5e70e64958b9",
                name="VM Delete",
            ),
            Role(
                uuid="4577db69-7c3e-4545-a9df-d8f6652347da",
                name="VM Create/Edit",
            ),
            Role(
                uuid="a1c67942-1ed4-4f8e-853c-76efa9efe5f1",
                name="VM Power Controls",
            ),
        ]

        role_uuids = user.get_role_uuids(module, rest_client)

        assert role_uuids == [
            "9524382c-a199-47cc-bc94-5e70e64958b9",
            "4577db69-7c3e-4545-a9df-d8f6652347da",
            "a1c67942-1ed4-4f8e-853c-76efa9efe5f1",
        ]


class TestDataForCreateUser:
    def test_data_for_create_user(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                status="present",
                username="username",
                password="password",
                full_name="fullname",
                roles=["VM delete", "VM Create/Edit", "VM Power Controls"],
                session_limit=2,
            ),
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.user.get_role_uuids"
        ).return_value = [
            "9524382c-a199-47cc-bc94-5e70e64958b9",
            "4577db69-7c3e-4545-a9df-d8f6652347da",
            "a1c67942-1ed4-4f8e-853c-76efa9efe5f1",
        ]

        data = user.data_for_create_user(module, rest_client)

        assert data == dict(
            username="username",
            password="password",
            fullName="fullname",
            roleUUIDs=[
                "9524382c-a199-47cc-bc94-5e70e64958b9",
                "4577db69-7c3e-4545-a9df-d8f6652347da",
                "a1c67942-1ed4-4f8e-853c-76efa9efe5f1",
            ],
            sessionLimit=2,
        )


class TestDataForUpdateUser:
    def test_data_for_update_user(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                status="present",
                username="username",
                username_new="updated_username",
                password="updated_password",
                full_name="updated_fullname",
                roles=["Admin"],
                session_limit=0,
            ),
        )
        my_user = User(
            uuid="38b346c6-a626-444b-b6ab-92ecd671afc0",
            username="username",
            full_name="fullname",
            role_uuids=[
                "9524382c-a199-47cc-bc94-5e70e64958b9",
                "4577db69-7c3e-4545-a9df-d8f6652347da",
                "a1c67942-1ed4-4f8e-853c-76efa9efe5f1",
            ],
            session_limit=2,
        )

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.user.get_role_uuids"
        ).return_value = ["38b346c6-a626-444b-b6ab-92ecd671afc0"]

        data = user.data_for_update_user(module, rest_client, my_user)

        assert data == dict(
            username="updated_username",
            password="updated_password",
            fullName="updated_fullname",
            roleUUIDs=["38b346c6-a626-444b-b6ab-92ecd671afc0"],
            sessionLimit=0,
        )


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            state="present",
            username="username",
            username_new="updated_username",
            password="updated_password",
            full_name="updated_fullname",
            roles=[
                "Backup",
                "VM Delete",
                "Cluster Settings",
                "Cluster Shutdown",
                "VM Power Controls",
                "Read",
                "VM Create/Edit",
                "Admin",
            ],
            session_limit=0,
        )
        success, result = run_main(user, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            state="absent",
            username="username",
        )
        success, result = run_main(user, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(user)

        assert success is False
        assert "missing required arguments: state, username" in result["msg"]
