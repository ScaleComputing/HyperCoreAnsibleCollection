# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import user_info

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRun:
    def test_run_all_users(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                username=None,
            ),
        )
        rest_client.list_records.return_value = [
            dict(
                fullName="fullname",
                roleUUIDs=[
                    "51e6d073-7566-4273-9196-58720117bd7f",
                    "7224a2bd-5a08-4b99-a0de-9977089c66a4",
                ],
                sessionLimit=0,
                username="username",
                uuid="51e6d073-7566-4273-9196-58720117bd7f",
            ),
            dict(
                fullName="admin",
                roleUUIDs=[
                    "51e6d073-7566-4273-9196-58720117bd7f",
                ],
                sessionLimit=0,
                username="admin",
                uuid="7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ),
        ]

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.user_info.User.to_ansible"
        ).side_effect = [
            {
                "fullname": "fullname",
                "roles": [
                    {
                        "name": "Cluster Settings",
                        "uuid": "51e6d073-7566-4273-9196-58720117bd7f",
                    },
                    {
                        "name": "Cluster Shutdown",
                        "uuid": "7224a2bd-5a08-4b99-a0de-9977089c66a4",
                    },
                ],
                "session_limit": 0,
                "username": "username",
                "uuid": "51e6d073-7566-4273-9196-58720117bd7f",
            },
            {
                "fullname": "admin",
                "roles": [
                    {"name": "Admin", "uuid": "51e6d073-7566-4273-9196-58720117bd7f"},
                ],
                "session_limit": 0,
                "username": "admin",
                "uuid": "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            },
        ]

        result = user_info.run(module, rest_client)

        rest_client.list_records.assert_called_with("/rest/v1/User", {})
        assert result == [
            {
                "fullname": "fullname",
                "roles": [
                    {
                        "name": "Cluster Settings",
                        "uuid": "51e6d073-7566-4273-9196-58720117bd7f",
                    },
                    {
                        "name": "Cluster Shutdown",
                        "uuid": "7224a2bd-5a08-4b99-a0de-9977089c66a4",
                    },
                ],
                "session_limit": 0,
                "username": "username",
                "uuid": "51e6d073-7566-4273-9196-58720117bd7f",
            },
            {
                "fullname": "admin",
                "roles": [
                    {"name": "Admin", "uuid": "51e6d073-7566-4273-9196-58720117bd7f"},
                ],
                "session_limit": 0,
                "username": "admin",
                "uuid": "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            },
        ]

    def test_run_selected_user(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                username="admin",
            ),
        )
        rest_client.list_records.return_value = [
            dict(
                fullName="admin",
                roleUUIDs=[
                    "51e6d073-7566-4273-9196-58720117bd7f",
                ],
                sessionLimit=0,
                username="admin",
                uuid="7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ),
        ]

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.user_info.User.to_ansible"
        ).return_value = {
            "fullname": "admin",
            "roles": [
                {"name": "Admin", "uuid": "51e6d073-7566-4273-9196-58720117bd7f"},
            ],
            "session_limit": 0,
            "username": "admin",
            "uuid": "7224a2bd-5a08-4b99-a0de-9977089c66a4",
        }

        result = user_info.run(module, rest_client)

        rest_client.list_records.assert_called_with(
            "/rest/v1/User", {"username": "admin"}
        )
        assert result == [
            {
                "fullname": "admin",
                "roles": [
                    {"name": "Admin", "uuid": "51e6d073-7566-4273-9196-58720117bd7f"},
                ],
                "session_limit": 0,
                "username": "admin",
                "uuid": "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            },
        ]

    def test_run_records_absent(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                username="admin",
            ),
        )
        rest_client.list_records.return_value = []

        result = user_info.run(module, rest_client)
        assert result == []


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
            username="admin",
        )

        success, result = run_main(user_info, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                username="admin",
                password="admin",
            ),
        )

        success, result = run_main(user_info, params)

        assert success is True
