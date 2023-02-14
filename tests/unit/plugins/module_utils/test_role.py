from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.role import Role
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRole:
    def test_role_from_hypercore_dict_not_empty(self):
        role = Role(
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )

        hypercore_dict = dict(
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )

        role_from_hypercore = Role.from_hypercore(hypercore_dict)
        assert role == role_from_hypercore

    def test_role_from_hypercore_dict_empty(self):
        assert Role.from_hypercore([]) is None

    def test_role_to_ansible(self):
        role = Role(
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )

        ansible_dict = dict(
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )

        assert role.to_ansible() == ansible_dict

    def test_role_equal_true(self):
        role1 = Role(
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )
        role2 = Role(
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )

        assert role1 == role2

    def test_role_equal_false(self):
        role1 = Role(
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )
        role2 = Role(
            name="name",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )

        assert role1 != role2

    def test_get_role_from_uuid(self, rest_client):
        role_uuid = "51e6d073-7566-4273-9196-58720117bd7f"
        rest_client.get_record.return_value = dict(
            name="Admin",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        role_from_hypercore = Role.get_role_from_uuid(role_uuid, rest_client)

        rest_client.get_record.assert_called_with(
            "/rest/v1/Role/51e6d073-7566-4273-9196-58720117bd7f",
            must_exist=False,
        )
        assert role_from_hypercore == Role(
            name="Admin",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

    def test_get_role_from_name(self, rest_client):
        role_name = "Admin"
        rest_client.get_record.return_value = dict(
            name="Admin",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )

        role_from_hypercore = Role.get_role_from_name(role_name, rest_client)

        rest_client.get_record.assert_called_with(
            "/rest/v1/Role",
            {"name": "Admin"},
            must_exist=False,
        )
        assert role_from_hypercore == Role(
            name="Admin",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
        )
