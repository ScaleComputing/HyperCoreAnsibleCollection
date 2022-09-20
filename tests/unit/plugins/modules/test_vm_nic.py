# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_nic

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestEnsureAbsent:
    @classmethod
    def _get_empty_test_vm(cls):
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_uuid",
        }

    @classmethod
    def _get_test_vm(cls):
        nic_dict_1 = {
            "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 1,
            "type": "virtio",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        nic_dict_2 = {
            "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
            "virDomainUUID": "8542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "vlan": 2,
            "type": "RTL8139",
            "connected": True,
            "ipv4Addresses": ["10.0.0.1", "10.0.0.2"],
            "macAddress": "00-00-00-00-00",
        }
        return {
            "uuid": "7542f2gg-5f9a-51ff-8a91-8ceahgf47ghg",
            "nodeUUID": "",
            "name": "XLAB_test_vm",
            "blockDevs": [],
            "netDevs": [nic_dict_1, nic_dict_2],
            "stats": "bla",
            "tags": "XLAB,test",
            "description": "test vm",
            "mem": 23424234,
            "state": "RUNNING",
            "numVCPU": 2,
            "bootDevices": [],
            "operatingSystem": "windows",
            "affinityStrategy": {
                "strictAffinity": False,
                "preferredNodeUUID": "",
                "backupNodeUUID": "",
            },
            "snapshotScheduleUUID": "snapshot_schedule_uuid",
        }

    def test_ensure_absent_when_no_change(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[],
                state="absent",
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        rest_client.list_records.return_value = [self._get_empty_test_vm()]
        rest_client.create_record.return_value = {"taskTag": "1234"}
        results = vm_nic.ensure_absent(module=module, rest_client=rest_client)
        print(results)
        assert results == (False, [], {"before": [], "after": []}, False)

    def test_ensure_absent_when_change(self, create_module, rest_client, mocker):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username="admin",
                    password="admin",
                ),
                vm_name="XLAB_test_vm",
                items=[{"vlan": 1}, {"vlan": 2}],
                state="absent",
            )
        )
        rest_client.delete_record.side_effect = [
            {"taskTag": "1234", "createdUUID": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
            {"taskTag": "5678", "createdUUID": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab"},
        ]
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.Node.get_node"
        ).return_value = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.SnapshotSchedule.get_snapshot_schedule"
        ).return_value = None
        rest_client.list_records.return_value = [self._get_test_vm()]
        rest_client.get_record.return_value = {"state": "COMPLETED"}
        rest_client.create_record.return_value = {"taskTag": "1234"}
        results = vm_nic.ensure_absent(module=module, rest_client=rest_client)
        print(results)
        assert results == (
            True,
            [None, None],
            {
                "before": [
                    {
                        "uuid": "6756f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 1,
                        "type": "virtio",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                    {
                        "uuid": "6456f2hj-6u9a-90ff-6g91-7jeahgf47aab",
                        "vlan": 2,
                        "type": "RTL8139",
                        "connected": True,
                        "ipv4_addresses": ["10.0.0.1", "10.0.0.2"],
                        "mac": "00-00-00-00-00",
                    },
                ],
                "after": [None, None],
            },
            True,
        )


class TestMain:
    def test_minimal_set_of_params(self, run_main_with_reboot):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            state="present",
            vm_name=dict(
                type="str",
                required=True,
            ),
            items=[],
        )

        success, results = run_main_with_reboot(vm_nic, params)

        assert success is True
        assert results == {
            "changed": False,
            "records": {},
            "diff": {"before": {}, "after": {}},
            "vm_rebooted": False,
        }
