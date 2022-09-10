from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_info

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRun:
    def test_run_records_present(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-unique-name",
            ),
        )

        rest_client.list_records.return_value = [
            dict(
                uuid="id",
                nodeUUID="node_id",
                name="VM-unique-name",
                tags="XLAB-test-tag1,XLAB-test-tag2",
                description="desc",
                mem=42,
                state="RUNNING",
                numVCPU=2,
                netDevs=[],
                blockDevs=[],
                cloudInitData=None,
                bootDevices=[],
                attachGuestToolsISO=False,
                operatingSystem=None,
                latestTaskTag=None,
                desiredDisposition=None,
                affinityStrategy={
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
                snapshotScheduleUUID="snapshot_schedule_id",
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        result = vm_info.run(module, rest_client)

        assert result == [
            {
                "attach_guest_tools_iso": False,
                "boot_devices": [],
                "description": "desc",
                "disks": [],
                "memory": 42,
                "nics": [],
                "node_affinity": {
                    "backup_node": {
                        "backplane_ip": "",
                        "lan_ip": "",
                        "node_uuid": "",
                        "peer_id": None,
                    },
                    "preferred_node": {
                        "backplane_ip": "",
                        "lan_ip": "",
                        "node_uuid": "",
                        "peer_id": None,
                    },
                    "strict_affinity": False,
                },
                "operating_system": None,
                "power_state": "started",
                "snapshot_schedule": None,
                "tags": ["XLAB-test-tag1", "XLAB-test-tag2"],
                "uuid": "id",
                "vcpu": 2,
                "vm_name": "VM-unique-name",
            }
        ]

    def test_run_records_absent(self, create_module, rest_client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="VM-unique-name",
                uuid="id",
            ),
        )

        rest_client.list_records.return_value = []
        result = vm_info.run(module, rest_client)
        assert result == []
