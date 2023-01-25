from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.role import Role

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
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
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )

        role_from_hypercore = Role.get_role_from_uuid(role_uuid, rest_client)

        assert role_from_hypercore == Role(
            name="admin",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
        )
