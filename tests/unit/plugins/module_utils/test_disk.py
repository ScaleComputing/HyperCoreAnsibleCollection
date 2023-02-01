from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.disk import Disk
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM
from ansible_collections.scale_computing.hypercore.plugins.module_utils.errors import (
    ScaleComputingError,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestDisk:
    def test_disk_from_ansible_no_type_new(self):
        ansible_dict = dict(
            type="virtio_disk",
            disk_slot=0,
            size=4200,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            iso_name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=4,
            mount_points=[],
            read_only=False,
        )

        disk = Disk(
            type="virtio_disk",
            slot=0,
            cache_mode="none",
            size=4200,
            uuid="id",
            name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=4,
            mount_points=[],
            read_only=False,
        )

        disk_from_ansible = Disk.from_ansible(ansible_dict)
        assert disk == disk_from_ansible

    def test_disk_from_ansible_type_new(self):
        ansible_dict = dict(
            type="virtio_disk-will-not-get-considered",
            type_new="virtio-disk",
            disk_slot=0,
            size=4200,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            iso_name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=4,
            mount_points=[],
            read_only=False,
        )

        disk = Disk(
            type="virtio-disk",
            slot=0,
            cache_mode="none",
            size=4200,
            name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=4,
            mount_points=[],
            read_only=False,
            uuid="id",
        )

        disk_from_ansible = Disk.from_ansible(ansible_dict)
        assert disk == disk_from_ansible

    def test_disk_from_hypercore_dict_not_empty_success(self):
        disk = Disk(
            type="virtio_disk",
            slot=0,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            size=4200,
            name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=4,
            mount_points=[],
            read_only=False,
        )

        hypercore_dict = dict(
            uuid="id",
            virDomainUUID="vm-id",
            type="VIRTIO_DISK",
            cacheMode="NONE",
            capacity=4200,
            slot=0,
            name="jc1-disk-0",
            disableSnapshotting=False,
            tieringPriorityFactor=8,
            mountPoints=[],
            readOnly=False,
        )

        disk_from_hypercore = Disk.from_hypercore(hypercore_dict)
        assert disk == disk_from_hypercore

    def test_disk_from_hypercore_dict_not_empty_missing_name(self):
        # tjazsch: Added example of where the field is missing.
        hypercore_dict = dict(
            uuid="id",
            virDomainUUID="vm-id",
            type="VIRTIO_DISK",
            cacheMode="NONE",
            capacity=4200,
            slot=0,
            disableSnapshotting=False,
            tieringPriorityFactor=8,
            mountPoints=[],
            readOnly=False,
        )

        with pytest.raises(ScaleComputingError, match="name"):
            Disk.from_hypercore(hypercore_dict)

    def test_disk_from_hypercore_dict_empty(self):
        assert Disk.from_hypercore([]) is None

    def test_disk_to_hypercore(self):
        disk = Disk(
            type="virtio_disk",
            slot=0,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            size=4200,
            name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=4,
            mount_points=[],
            read_only=False,
        )

        hypercore_dict = dict(
            uuid="id",
            virDomainUUID="vm-id",
            type="VIRTIO_DISK",
            cacheMode="NONE",
            capacity=4200,
            slot=0,
            name="jc1-disk-0",
            disableSnapshotting=False,
            tieringPriorityFactor=8,
            mountPoints=[],
            readOnly=False,
        )

        assert disk.to_hypercore() == hypercore_dict

    def test_disk_to_ansible(self):
        ansible_dict = dict(
            type="virtio_disk",
            disk_slot=0,
            size=4200,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            iso_name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=8,
            mount_points=[],
            read_only=False,
        )

        disk = Disk(
            type="virtio_disk",
            slot=0,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            size=4200,
            name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=8,
            mount_points=[],
            read_only=False,
        )

        disk_to_ansible = disk.to_ansible()
        assert disk_to_ansible == ansible_dict

    def test_equal(self):
        disk1 = Disk(
            type="virtio_disk",
            slot=0,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            size=4200,
            name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=8,
            mount_points=[],
            read_only=False,
        )

        disk2 = Disk(
            type="virtio_disk",
            slot=0,
            uuid="id",
            vm_uuid="vm-id",
            cache_mode="none",
            size=4200,
            name="jc1-disk-0",
            disable_snapshotting=False,
            tiering_priority_factor=8,
            mount_points=[],
            read_only=False,
        )

        assert disk1 == disk2

    def test_post_and_patch_payload(self):
        vm = VM(
            uuid="id",
            name="VM-name",
            memory=42,
            vcpu=2,
        )

        disk = Disk(
            type="virtio_disk",
            slot=0,
            cache_mode="none",
            size=4200,
            disable_snapshotting=False,
            tiering_priority_factor=4,
            read_only=False,
        )

        payload = disk.post_and_patch_payload(vm)

        assert payload == {
            "cacheMode": "NONE",
            "capacity": 4200,
            "disableSnapshotting": False,
            "readOnly": False,
            "slot": 0,
            "tieringPriorityFactor": 8,
            "type": "VIRTIO_DISK",
            "virDomainUUID": "id",
        }
