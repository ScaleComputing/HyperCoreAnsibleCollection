# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.user import User
from ansible_collections.scale_computing.hypercore.plugins.module_utils.role import Role
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestUser:
    def test_user_from_hypercore_dict_not_empty(self):
        user = User(
            full_name="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        hypercore_dict = dict(
            fullName="fullname",
            password="",
            roleUUIDs=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            sessionLimit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        user_from_hypercore = User.from_hypercore(hypercore_dict)
        assert user == user_from_hypercore

    def test_user_from_hypercore_dict_empty(self):
        assert User.from_hypercore([]) is None

    def test_user_to_ansible(self, mocker, rest_client):
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.user.Role.get_role_from_uuid"
        ).side_effect = [
            Role(name="Cluster Settings", uuid="38b346c6-a626-444b-b6ab-92ecd671afc0"),
            Role(name="Cluster Shutdown", uuid="7224a2bd-5a08-4b99-a0de-9977089c66a4"),
        ]

        user = User(
            full_name="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        ansible_dict = dict(
            full_name="fullname",
            roles=[
                dict(
                    name="Cluster Settings", uuid="38b346c6-a626-444b-b6ab-92ecd671afc0"
                ),
                dict(
                    name="Cluster Shutdown", uuid="7224a2bd-5a08-4b99-a0de-9977089c66a4"
                ),
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        assert user.to_ansible(rest_client) == ansible_dict

    def test_user_equal_true(self):
        user1 = User(
            full_name="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )
        user2 = User(
            full_name="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        assert user1 == user2

    def test_user_equal_false(self):
        user1 = User(
            full_name="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )
        user2 = User(
            full_name="",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        assert user1 != user2

    def test_get_user_from_username(self, rest_client):
        username = "my_name"
        rest_client.get_record.return_value = dict(
            fullName="fullname",
            roleUUIDs=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            sessionLimit=0,
            username="my_name",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        user = User.get_user_from_username(username, rest_client)

        rest_client.get_record.assert_called_with(
            "/rest/v1/User",
            {"username": "my_name"},
            must_exist=False,
        )
        assert user == User(
            full_name="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="my_name",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

    def test_get_user_from_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(
            fullName="fullname",
            roleUUIDs=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            sessionLimit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )
        user_uuid = "51e6d073-7566-4273-9196-58720117bd7f"
        user = User.get_user_from_uuid(user_uuid, rest_client)

        rest_client.get_record.assert_called_with(
            "/rest/v1/User/51e6d073-7566-4273-9196-58720117bd7f",
            must_exist=False,
        )
        assert user == User(
            full_name="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )
