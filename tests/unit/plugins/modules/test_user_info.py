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
    def test_run_records_present(self, rest_client):
        rest_client.list_records.return_value = [
            dict(
                fullName="fullname",
                roleUUIDs=[
                    "38b346c6-a626-444b-b6ab-92ecd671afc0",
                    "7224a2bd-5a08-4b99-a0de-9977089c66a4",
                ],
                sessionLimit=0,
                username="username",
                uuid="51e6d073-7566-4273-9196-58720117bd7f",
            )
        ]

        result = user_info.run(rest_client)
        assert result == [
            {
                "fullname": "fullname",
                "role_uuids": [
                    "38b346c6-a626-444b-b6ab-92ecd671afc0",
                    "7224a2bd-5a08-4b99-a0de-9977089c66a4",
                ],
                "session_limit": 0,
                "username": "username",
                "uuid": "51e6d073-7566-4273-9196-58720117bd7f",
            }
        ]

    def test_run_records_absent(self, rest_client):
        rest_client.list_records.return_value = []

        result = user_info.run(rest_client)
        assert result == []
