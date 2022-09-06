from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.iso import ISO

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestISO:
    def test_iso_from_ansible(self):
        ansible_dict = dict(
            name="ISO-test-name",
            size=42,
        )

        iso = ISO(
            name="ISO-test-name",
            size=42,
        )

        iso_from_ansible = ISO.from_ansible(ansible_dict)
        assert iso == iso_from_ansible

    def test_iso_from_hypercore_dict_not_empty(self):
        iso = ISO(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            mounts=[
                dict(vm_name="vm-name-1", vm_uuid="vm-uuid-1"),
                dict(vm_name="vm-name-2", vm_uuid="vm-uuid-2"),
            ],
            ready_for_insert=False,
            path="scribe",
        )

        hypercore_dict = dict(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            mounts=[
                dict(vmName="vm-name-1", vmUUID="vm-uuid-1"),
                dict(vmName="vm-name-2", vmUUID="vm-uuid-2"),
            ],
            readyForInsert=False,
            path="scribe",
        )

        iso_from_hypercore = ISO.from_hypercore(hypercore_dict)
        assert iso == iso_from_hypercore

    def test_iso_from_hypercore_dict_empty(self):
        assert ISO.from_hypercore([]) is None

    def test_iso_to_hypercore(self):
        iso = ISO(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            ready_for_insert=False,
            path="scribe",
        )

        hypercore_dict = dict(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            readyForInsert=False,
            path="scribe",
        )

        assert iso.to_hypercore() == hypercore_dict

    def test_iso_to_ansible(self):
        iso = ISO(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            mounts=[
                dict(vm_name="vm-name-1", vm_uuid="vm-uuid-1"),
                dict(vm_name="vm-name-2", vm_uuid="vm-uuid-2"),
            ],
            ready_for_insert=False,
        )

        ansible_dict = dict(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            mounts=[
                dict(vm_name="vm-name-1", vm_uuid="vm-uuid-1"),
                dict(vm_name="vm-name-2", vm_uuid="vm-uuid-2"),
            ],
            ready_for_insert=False,
            path=None,
        )

        assert iso.to_ansible() == ansible_dict

    def test_equal_true(self):
        iso1 = ISO(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            mounts=[
                dict(vm_name="vm-name-1", vm_uuid="vm-uuid-1"),
                dict(vm_name="vm-name-2", vm_uuid="vm-uuid-2"),
            ],
            ready_for_insert=False,
        )

        iso2 = ISO(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            mounts=[
                dict(vm_name="vm-name-1", vm_uuid="vm-uuid-1"),
                dict(vm_name="vm-name-2", vm_uuid="vm-uuid-2"),
            ],
            ready_for_insert=False,
        )

        assert iso1 == iso2

    def test_build_iso_post_paylaod(self):
        iso = ISO(
            uuid="id",
            name="ISO-test-name",
            size=8000,
            mounts=[
                dict(vm_name="vm-name-1", vm_uuid="vm-uuid-1"),
                dict(vm_name="vm-name-2", vm_uuid="vm-uuid-2"),
            ],
            ready_for_insert=False,
        )

        assert iso.build_iso_post_paylaod() == dict(
            name="ISO-test-name", size=8000, readyForInsert=False
        )

    def test_get_by_name(self, rest_client):
        ansible_dict = dict(
            vm_name="vm-name",
        )
        rest_client.get_record.return_value = dict(
            name="iso-image-name",
            readyForInsert=True,
            uuid="id",
            size=1234,
            mounts=[],
            path="scribe",
        )

        iso_image = ISO(
            name="iso-image-name",
            ready_for_insert=True,
            uuid="id",
            size=1234,
            mounts=[],
            path="scribe",
        )

        assert ISO.get_by_name(ansible_dict, rest_client) == iso_image
