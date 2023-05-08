# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    virtual_disk_attach,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM
from ansible_collections.scale_computing.hypercore.plugins.module_utils.disk import Disk
from ansible_collections.scale_computing.hypercore.plugins.module_utils.virtual_disk import (
    VirtualDisk,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


@pytest.fixture
def virtual_machine():
    return VM(
        uuid="f847daa6-80f3-4042-a016-ee56186939f7",
        name="vm_name",
        memory=1024,
        vcpu=4,
        disks=[Disk(type="virtio_disk", slot=0), Disk(type="virtio_disk", slot=1)],
    )


@pytest.fixture
def virtual_disk():
    return VirtualDisk(
        name="foobar.qcow2",
        uuid="e847315d-4e54-4265-bece-3e94c0749d42",
        block_size=1048576,
        size=104857600,
        replication_factor=2,
    )


class TestIsSlotAvailable:
    @pytest.mark.parametrize(
        "disk_slot, expected_result",
        [
            (1, (False, Disk(type="virtio_disk", slot=1))),
            (5, (True, None)),
        ],
    )
    def test_is_slot_available(
        self, create_module, disk_slot, expected_result, virtual_machine
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="foobar.qcow2",
                vm_name="XLAB_test_attach",
                disk=dict(disk_slot=disk_slot, type="virtio_disk"),
            )
        )

        assert expected_result == virtual_disk_attach.is_slot_available(
            module, virtual_machine
        )


class TestCreatePayload:
    def test_create_payload(self, create_module, virtual_machine, virtual_disk):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="foobar.qcow2",
                vm_name="XLAB_test_attach",
                disk=dict(
                    disk_slot=3,
                    size=645922816,
                    type="virtio_disk",
                    cache_mode="writethrough",
                    disable_snapshotting=False,
                    tiering_priority_factor=8,
                    read_only=True,
                    regenerate_disk_id=False,
                ),
            )
        )

        payload = virtual_disk_attach.create_payload(
            module, virtual_machine, virtual_disk
        )

        assert payload == dict(
            options={"regenerateDiskID": False, "readOnly": True},
            template={
                "virDomainUUID": "f847daa6-80f3-4042-a016-ee56186939f7",
                "type": "VIRTIO_DISK",
                "cacheMode": "WRITETHROUGH",
                "capacity": 645922816,
                "slot": 3,
                "disableSnapshotting": False,
                "tieringPriorityFactor": 128,
            },
        )

    def test_create_payload_min_params(
        self, create_module, virtual_machine, virtual_disk
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                name="foobar.qcow2",
                vm_name="XLAB_test_attach",
                disk=dict(
                    disk_slot=1,
                    size=None,  # default virtual_disk.size
                    type="virtio_disk",
                    cache_mode=None,
                    disable_snapshotting=None,
                    tiering_priority_factor=4,
                    read_only=False,
                    regenerate_disk_id=True,
                ),
            )
        )

        payload = virtual_disk_attach.create_payload(
            module, virtual_machine, virtual_disk
        )

        assert payload == dict(
            options={
                "readOnly": False,
                "regenerateDiskID": True,
            },
            template={
                "virDomainUUID": "f847daa6-80f3-4042-a016-ee56186939f7",
                "type": "VIRTIO_DISK",
                "slot": 1,
                "capacity": virtual_disk.size,
                "tieringPriorityFactor": 8,
            },
        )
