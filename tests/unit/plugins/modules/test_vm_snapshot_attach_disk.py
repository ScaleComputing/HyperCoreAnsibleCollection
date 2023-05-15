# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest import mock

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot import (
    VMSnapshot,
)

from ansible_collections.scale_computing.hypercore.plugins.modules import (
    vm_snapshot_attach_disk,
)

from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)

BLOCK_DEVICE = dict(
    uuid="new-block-uuid",
    size=100000595968,
    disk_slot=21,
    type="ide_disk",
    vm_uuid="vm-uuid-destination",
)

PARAMS = dict(
    cluster_instance=dict(
        host="https://0.0.0.0",
        username="admin",
        password="admin",
    ),
    vm_name="vm-destination",
    vm_disk_type="ide_disk",
    vm_disk_slot=42,
    source_snapshot_uuid="snapshot-uuid",
    source_disk_type="virtio_disk",
    source_disk_slot=0,
)


class TestAttachDisk:
    def setup_method(self):
        self.vm_snapshot = VMSnapshot(
            snapshot_uuid="snapshot-uuid",
            vm={
                "name": "vm-source",
                "uuid": "vm-uuid-source",
                "snapshot_serial_number": 1,
                "disks": [
                    {
                        "cache_mode": "writethrough",
                        "size": 100,
                        "disable_snapshotting": False,
                        "read_only": False,
                        "disk_slot": 0,
                        "iso_name": "test-iso.iso",
                        "tiering_priority_factor": 8,
                        "type": "virtio_disk",
                        "uuid": "snapshot-block-uuid-1",
                    },
                ],
            },
            device_snapshots=[
                {
                    "uuid": "block-uuid-1",
                },
            ],
            timestamp=123,
            label="snapshot",
            type="USER",
            automated_trigger_timestamp=111,
            local_retain_until_timestamp=222,
            remote_retain_until_timestamp=333,
            block_count_diff_from_serial_number=444,
            replication=True,
        )

        self.magic = mock.MagicMock()

    @pytest.mark.parametrize(
        ("destination_vm_disk_info", "expected_return"),
        [
            (None, (True, BLOCK_DEVICE, dict(before=None, after=BLOCK_DEVICE))),
            (
                BLOCK_DEVICE,
                (False, BLOCK_DEVICE, dict(before=BLOCK_DEVICE, after=None)),
            ),
        ],
    )
    def test_attach_disk_is_change(
        self,
        create_module,
        rest_client,
        task_wait,
        mocker,
        destination_vm_disk_info,
        expected_return,
    ):
        module = create_module(PARAMS)

        task_tag = {
            "taskTag": 123,
            "createdUUID": "new-block-uuid",
        }

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.get_snapshot_by_uuid"
        ).return_value = self.vm_snapshot
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.get_external_vm_uuid"
        ).return_value = "vm-uuid-destination"
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.get_vm_disk_info"
        ).return_value = destination_vm_disk_info

        rest_client.create_record.return_value = task_tag

        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.get_vm_disk_info_by_uuid"
        ).return_value = expected_return[1]

        called_with_dict = dict(
            endpoint="/rest/v1/VirDomainBlockDevice/snapshot-block-uuid-1/clone",
            payload=dict(
                options=dict(
                    regenerateDiskID=True,  # required
                    readOnly=False,  # required
                ),
                snapUUID="snapshot-uuid",
                template=dict(
                    virDomainUUID="vm-uuid-destination",  # required
                    type="IDE_DISK",  # required
                    capacity=100,  # required
                    chacheMode="WRITETHROUGH",
                    slot=42,
                    disableSnapshotting=False,
                    tieringPriorityFactor=8,
                ),
            ),
            check_mode=False,
        )

        changed, record, diff = vm_snapshot_attach_disk.attach_disk(module, rest_client)

        if destination_vm_disk_info is None:
            rest_client.create_record.assert_called_once_with(**called_with_dict)
        else:
            rest_client.create_record.assert_not_called()

        assert changed == expected_return[0]
        assert record == expected_return[1]
        assert diff == expected_return[2]


class TestMain:
    def test_fail(self, run_main):
        success, result = run_main(vm_snapshot_attach_disk)

        assert success is False
        assert "missing required arguments" in result["msg"]

    def test_params(self, run_main):
        success, result = run_main(vm_snapshot_attach_disk, PARAMS)
        assert success is True
