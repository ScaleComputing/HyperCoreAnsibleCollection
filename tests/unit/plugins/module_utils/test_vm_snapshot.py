# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest
import datetime
from datetime import date

from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot import (
    VMSnapshot,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


# Test calculate_data() static method.
class TestCalculateDate:
    @pytest.mark.parametrize(
        "days, expected_output",
        [
            (1, (datetime.datetime.today().date() + datetime.timedelta(days=1))),
            (0, None),
            (None, None),
        ],
    )
    def test_calculate_date(self, days, expected_output):
        result = VMSnapshot.calculate_date(days)
        if result:  # If not None or 0 convert to date.
            result = date.fromtimestamp(result)
        assert result == expected_output
HYPERCORE_PROTOCOL_TCP = "SYSLOG_PROTOCOL_TCP"
ANSIBLE_PROTOCOL_TCP = "tcp"


class TestVMSnapshot:
    def setup_method(self):
        self.vm = {
            "name": "test-vm",
            "uuid": "vm-uuid",
            "snapshot_serial_number": 1,
            "block_devices": [
                {
                    "cache_mode": "WRITETHROUGH",
                    "capacity": 100,
                    "disable_snapshotting": False,
                    "read_only": False,
                    "slot": 0,
                    "tiering_priority_factor": 8,
                    "type": "VIRTIO_DISK",
                    "uuid": "block-uuid-1"
                },
            ]
        }

        self.device_snapshots = [
            {
                "uuid": "block-uuid-1"
            },
        ],

        self.vm_snapshot = VMSnapshot(
            snapshot_uuid="test",
            vm=self.vm,
            device_snapshots=self.device_snapshots,
            timestamp=123,
            label="snapshot",
            type="USER",
            automated_trigger_timestamp=111,
            local_retain_until_timestamp=222,
            remote_retain_until_timestamp=333,
            block_count_diff_from_serial_number=444,
            replication=True,
        )
        self.from_hypercore_dict = dict(
            uuid=self.vm_snapshot.snapshot_uuid,
            domain={
                "name": self.vm_snapshot.vm.name,
                "domainUUID": self.vm_snapshot.vm.uuid,
                "snapshotSerialNumber": self.vm_snapshot.vm.snapshot_serial_number,
                "blockDevs": {
                    "cacheMode": "WRITETHROUGH",
                    "capacity": 100,
                    "disableSnapshotting": False,
                    "readOnly": False,
                    "slot": 0,
                    "tieringPriorityFactor": 8,
                    "type": "VIRTIO_DISK",
                    "uuid": "block-uuid-1"
                },
            },
            host="0.0.0.0",
            port=42,
            protocol=HYPERCORE_PROTOCOL_TCP,
            resendDelay=123,
            silentPeriod=123,
            latestTaskTag={},
        )
        self.to_hypercore_dict = dict(
            snapshot_uuid=self.vm_snapshot.snapshot_uuid,
            vm=self.vm_snapshot.vm,
            label=self.vm_snapshot.label,
            type=self.vm_snapshot.type,
        )
        self.ansible_dict = dict(
            snapshot_uuid=self.vm_snapshot.snapshot_uuid,
            vm=self.vm_snapshot.vm,
            device_snapshots=self.vm_snapshot.device_snapshots,
            timestamp=self.vm_snapshot.timestamp,
            label=self.vm_snapshot.label,
            type=self.vm_snapshot.type,
            automated_trigger_timestamp=self.vm_snapshot.automated_trigger_timestamp,
            local_retain_until_timestamp=self.vm_snapshot.local_retain_until_timestamp,
            remote_retain_until_timestamp=self.vm_snapshot.remote_retain_until_timestamp,
            block_count_diff_from_serial_number=self.vm_snapshot.block_count_diff_from_serial_number,
            replication=self.vm_snapshot.replication,
        )

    def test_vm_snapshot_to_hypercore(self):
        assert self.vm_snapshot.to_hypercore() == self.to_hypercore_dict

    def test_syslog_server_from_hypercore_dict_not_empty(self):
        syslog_server_from_hypercore = SyslogServer.from_hypercore(
            self.from_hypercore_dict
        )
        assert self.syslog_server == syslog_server_from_hypercore

    def test_syslog_server_from_hypercore_dict_empty(self):
        assert SyslogServer.from_hypercore([]) is None

    def test_syslog_server_to_ansible(self):
        assert self.syslog_server.to_ansible() == self.ansible_dict

    def test_syslog_server_from_ansible(self):
        syslog_server_from_ansible = SyslogServer.from_ansible(self.ansible_dict)
        assert syslog_server_from_ansible == SyslogServer(
            uuid=syslog_server_from_ansible.uuid,
            host=syslog_server_from_ansible.host,
            port=syslog_server_from_ansible.port,
            protocol=syslog_server_from_ansible.protocol,
        )

    def test_get_by_uuid(self, rest_client):
        rest_client.get_record.return_value = dict(**self.from_hypercore_dict)
        ansible_dict = dict(
            uuid="test",
        )
        syslog_server_from_hypercore = SyslogServer.get_by_uuid(
            ansible_dict, rest_client
        )
        assert syslog_server_from_hypercore == self.syslog_server

    def test_get_state(self, rest_client):
        rest_client.list_records.return_value = [
            self.from_hypercore_dict,
            self.from_hypercore_dict,
        ]

        expected = {
            "uuid": "test",
            "alert_tag_uuid": "0",
            "host": "0.0.0.0",
            "port": 42,
            "protocol": ANSIBLE_PROTOCOL_TCP,
            "resend_delay": 123,
            "silent_period": 123,
            "latest_task_tag": {},
        }
        result = SyslogServer.get_state(rest_client)
        print(result)

        assert result == [expected, expected]

    def test_get_state_no_record(self, rest_client):
        rest_client.list_records.return_value = []

        result = SyslogServer.get_state(rest_client)
        assert result == []

    def test_get_by_host(self, rest_client):
        rest_client.get_record.return_value = dict(**self.from_hypercore_dict)

        result = SyslogServer.get_by_host("0.0.0.0", rest_client)
        assert result == self.syslog_server
