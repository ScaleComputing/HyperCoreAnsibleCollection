from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.snapshot_schedule import (
    SnapshotSchedule,
    Recurrence,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestSnapshotSchedule:
    def test_snapshot_schedule_from_ansible(self):
        ansible_dict = dict(
            name="snapshot-name",
            recurrences=[
                dict(
                    name="recurrence-name",
                    frequency="FREQ=WEEKLY",
                    start="2010-01-01 00:00:00",
                    local_retention=6048000,
                    remote_retention=6048000,
                    replication=True,
                )
            ],
        )

        snapshot_schedule = SnapshotSchedule(
            name="snapshot-name",
            recurrences=[
                Recurrence(
                    name="recurrence-name",
                    frequency="FREQ=WEEKLY",
                    start="2010-01-01 00:00:00",
                    local_retention=6048000,
                    remote_retention=6048000,
                    replication=True,
                )
            ],
        )

        snapshot_from_ansible = SnapshotSchedule.from_ansible(ansible_dict)

        assert snapshot_schedule == snapshot_from_ansible

    def test_snapshot_schedule_from_hypercore_dict_not_empty(self):
        snapshot_schedule = SnapshotSchedule(
            name="snapshot-name",
            uuid="id",
            recurrences=[
                Recurrence(
                    name="recurrence-name",
                    frequency="FREQ=WEEKLY",
                    start="2010-01-01 00:00:00",
                    local_retention=6048000,
                    remote_retention=6048000,
                    replication=True,
                    uuid="id",
                )
            ],
        )

        hypercore_dict = dict(
            name="snapshot-name",
            uuid="id",
            rrules=[
                dict(
                    name="recurrence-name",
                    rrule="FREQ=WEEKLY",
                    dtstart="2010-01-01 00:00:00",
                    localRetentionDurationSeconds=6048000,
                    remoteRetentionDurationSeconds=6048000,
                    replication=True,
                    uuid="id",
                )
            ],
        )

        snapshot_schedule_from_hypercore = SnapshotSchedule.from_hypercore(
            hypercore_dict
        )
        assert snapshot_schedule == snapshot_schedule_from_hypercore

    def test_snapshot_schedule_from_hypercore_dict_empty(self):
        assert SnapshotSchedule.from_hypercore([]) is None

    def test_snapshot_schedule_to_hypercore(self):
        snapshot_schedule = SnapshotSchedule(
            name="snapshot-name",
            uuid="id",
            recurrences=[
                Recurrence(
                    name="recurrence-name",
                    frequency="FREQ=WEEKLY",
                    start="2010-01-01 00:00:00",
                    local_retention=6048000,
                    remote_retention=6048000,
                    replication=True,
                    uuid="id",
                )
            ],
        )

        hypercore_dict = dict(
            name="snapshot-name",
            uuid="id",
            rrules=[
                dict(
                    name="recurrence-name",
                    rrule="FREQ=WEEKLY",
                    dtstart="2010-01-01 00:00:00",
                    localRetentionDurationSeconds=6048000,
                    remoteRetentionDurationSeconds=6048000,
                    replication=True,
                    uuid="id",
                )
            ],
        )

        assert snapshot_schedule.to_hypercore() == hypercore_dict

    def test_snapshot_schedule_to_ansible(self):
        snapshot_schedule = SnapshotSchedule(
            name="snapshot-name",
            uuid="id",
            recurrences=[
                Recurrence(
                    name="recurrence-name",
                    frequency="FREQ=WEEKLY",
                    start="2010-01-01 00:00:00",
                    local_retention=6048000,
                    remote_retention=6048000,
                    replication=True,
                    uuid="id",
                )
            ],
        )

        ansible_dict = dict(
            name="snapshot-name",
            uuid="id",
            recurrences=[
                dict(
                    name="recurrence-name",
                    frequency="FREQ=WEEKLY",
                    start="2010-01-01 00:00:00",
                    local_retention=6048000,
                    remote_retention=6048000,
                    replication=True,
                    uuid="id",
                )
            ],
        )

        assert snapshot_schedule.to_ansible() == ansible_dict

    def test_equal_true(self):
        snapshot_schedule1 = SnapshotSchedule(
            name="snapshot-name",
            uuid="id",
            recurrences=[
                Recurrence(
                    name="recurrence-name",
                    frequency="FREQ=WEEKLY",
                    start="2010-01-01 00:00:00",
                    local_retention=6048000,
                    remote_retention=6048000,
                    replication=True,
                    uuid="id",
                )
            ],
        )

        snapshot_schedule2 = SnapshotSchedule(
            name="snapshot-name",
            uuid="id",
            recurrences=[
                Recurrence(
                    name="recurrence-name",
                    frequency="FREQ=WEEKLY",
                    start="2010-01-01 00:00:00",
                    local_retention=6048000,
                    remote_retention=6048000,
                    replication=True,
                    uuid="id",
                )
            ],
        )

        assert snapshot_schedule1 == snapshot_schedule2

    def test_get_by_name(self, rest_client):
        ansible_dict = dict(
            name="snapshot-name",
        )

        rest_client.get_record.return_value = dict(
            name="snapshot-name",
            uuid="id",
            rrules=[],
        )

        snapshot_schedule_image = SnapshotSchedule(
            name="snapshot-name",
            uuid="id",
            recurrences=[],
        )

        assert (
            SnapshotSchedule.get_by_name(ansible_dict, rest_client)
            == snapshot_schedule_image
        )


class TestRecurrence:
    def test_recurrence_from_ansible(self):
        ansible_dict = dict(
            name="recurrence-name",
            frequency="FREQ=WEEKLY",
            start="2010-01-01 00:00:00",
            local_retention=6048000,
            remote_retention=6048000,
            replication=True,
        )

        recurrence = Recurrence(
            name="recurrence-name",
            frequency="FREQ=WEEKLY",
            start="2010-01-01 00:00:00",
            local_retention=6048000,
            remote_retention=6048000,
            replication=True,
        )

        assert recurrence == Recurrence.from_ansible(ansible_dict)

    def test_recurrence_from_hypercore_dict_not_empty(self):
        recurrence = Recurrence(
            name="recurrence-name",
            frequency="FREQ=WEEKLY",
            start="2010-01-01 00:00:00",
            local_retention=6048000,
            remote_retention=6048000,
            replication=True,
            uuid="id",
        )

        hypercore_dict = dict(
            name="recurrence-name",
            rrule="FREQ=WEEKLY",
            dtstart="2010-01-01 00:00:00",
            localRetentionDurationSeconds=6048000,
            remoteRetentionDurationSeconds=6048000,
            replication=True,
            uuid="id",
        )

        recurrence_from_hypercore = Recurrence.from_hypercore(hypercore_dict)
        assert recurrence == recurrence_from_hypercore

    def test_recurrence_from_hypercore_dict_empty(self):
        assert Recurrence.from_hypercore([]) is None

    def test_recurrence_to_hypercore(self):
        recurrence = Recurrence(
            name="recurrence-name",
            frequency="FREQ=WEEKLY",
            start="2010-01-01 00:00:00",
            local_retention=6048000,
            remote_retention=6048000,
            replication=True,
            uuid="id",
        )

        hypercore_dict = dict(
            name="recurrence-name",
            rrule="FREQ=WEEKLY",
            dtstart="2010-01-01 00:00:00",
            localRetentionDurationSeconds=6048000,
            remoteRetentionDurationSeconds=6048000,
            replication=True,
            uuid="id",
        )

        assert recurrence.to_hypercore() == hypercore_dict

    def test_recurrence_to_ansible(self):
        recurrence = Recurrence(
            name="recurrence-name",
            frequency="FREQ=WEEKLY",
            start="2010-01-01 00:00:00",
            local_retention=6048000,
            remote_retention=6048000,
            replication=True,
            uuid="id",
        )

        ansible_dict = dict(
            name="recurrence-name",
            frequency="FREQ=WEEKLY",
            start="2010-01-01 00:00:00",
            local_retention=6048000,
            remote_retention=6048000,
            replication=True,
            uuid="id",
        )

        assert recurrence.to_ansible() == ansible_dict

    def test_equal_true(self):
        recurrence1 = Recurrence(
            name="recurrence-name",
            frequency="FREQ=WEEKLY",
            start="2010-01-01 00:00:00",
            local_retention=6048000,
            remote_retention=6048000,
            replication=True,
            uuid="id",
        )

        recurrence2 = Recurrence(
            name="recurrence-name",
            frequency="FREQ=WEEKLY",
            start="2010-01-01 00:00:00",
            local_retention=6048000,
            remote_retention=6048000,
            replication=True,
            uuid="id",
        )

        assert recurrence1 == recurrence2
