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
                uuid="id",
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
                bootDevices=None,
                attachGuestToolsISO=False,
                operatingSystem=None,
                latestTaskTag=None,
                desiredDisposition=None,
                affinityStrategy={
                    "strictAffinity": False,
                    "preferredNodeUUID": "",
                    "backupNodeUUID": "",
                },
            ),
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None

        result = vm_info.run(module, rest_client)

        assert result == [
            dict(
                uuid="id",  # No uuid when creating object from ansible
                vm_name="VM-unique-name",
                tags=["XLAB-test-tag1", "XLAB-test-tag2"],
                description="desc",
                memory=42,
                power_state="started",
                vcpu=2,
                nics=[],
                disks=[],
                boot_devices=[],
                attach_guest_tools_iso=False,
                operating_system=None,
                node_affinity={
                    "strict_affinity": False,
                    "preferred_node": dict(
                        node_uuid=None,
                        backplane_ip=None,
                        lan_ip=None,
                        peer_id=None,
                    ),
                    "backup_node": dict(
                        node_uuid=None,
                        backplane_ip=None,
                        lan_ip=None,
                        peer_id=None,
                    ),
                },
            ),
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
