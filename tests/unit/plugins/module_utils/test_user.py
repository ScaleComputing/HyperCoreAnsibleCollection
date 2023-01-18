# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.user import User

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestUser:
    def test_user_from_hypercore_dict_not_empty(self):
        node = User(
            fullname="fullname",
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
            roleUUIDs=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            sessionLimit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        node_from_hypercore = User.from_hypercore(hypercore_dict)
        assert node == node_from_hypercore

    def test_user_from_hypercore_dict_empty(self):
        assert User.from_hypercore([]) is None

    def test_user_to_ansible(self):
        user = User(
            fullname="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        ansible_dict = dict(
            fullname="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        assert user.to_ansible() == ansible_dict

    def test_user_equal_true(self):
        user1 = User(
            fullname="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )
        user2 = User(
            fullname="fullname",
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
            fullname="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )
        user2 = User(
            fullname="",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        assert user1 != user2

    def test_get_user(self, rest_client):
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
        query = {"uuid": "51e6d073-7566-4273-9196-58720117bd7f"}
        node_from_hypercore = User.get_user(query, rest_client)

        assert node_from_hypercore == User(
            fullname="fullname",
            role_uuids=[
                "38b346c6-a626-444b-b6ab-92ecd671afc0",
                "7224a2bd-5a08-4b99-a0de-9977089c66a4",
            ],
            session_limit=0,
            username="username",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )
