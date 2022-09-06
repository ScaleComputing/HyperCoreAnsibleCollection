# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper
from ..module_utils.utils import get_query


class SnapshotSchedule(PayloadMapper):
    # Variables in SnapshotSchedule are written in ansible-native format
    def __init__(self, name, uuid=None, recurrences=None):
        self.name = name
        self.uuid = uuid
        # recurrences is list whose elements are instances of class Recurrence.
        self.recurrences = recurrences

    @classmethod
    def from_ansible(cls, vm_dict):
        return SnapshotSchedule(
            name=vm_dict["name"],
            recurrences=[
                Recurrence.from_ansible(recurrence_dict)
                for recurrence_dict in vm_dict.get("recurrences", [])
            ],
        )

    @classmethod
    def from_hypercore(cls, vm_dict):
        if not vm_dict:  # In case for get_record, return None if no result is found
            return None
        return SnapshotSchedule(
            name=vm_dict["name"],
            uuid=vm_dict["uuid"],
            recurrences=[
                Recurrence.from_hypercore(recurrence_dict)
                for recurrence_dict in vm_dict["rrules"]
            ],
        )

    def to_hypercore(self):
        return dict(
            name=self.name,
            uuid=self.uuid,
            rrules=[recurrence.to_hypercore() for recurrence in self.recurrences],
        )

    def to_ansible(self):
        return dict(
            name=self.name,
            uuid=self.uuid,
            recurrences=[recurrence.to_ansible() for recurrence in self.recurrences],
        )

    def __eq__(self, other):
        """One SnapshotSchedule is equal to another if it has ALL attributes exactly the same"""
        return all(
            (
                self.name == other.name,
                self.uuid == other.uuid,
                self.recurrences == other.recurrences,
            )
        )

    def __str__(self):
        return super().__str__()

    @classmethod
    def get_by_name(cls, ansible_dict, rest_client, must_exist=False):
        """
        With given dict from playbook, finds the existing SnapshotSchedule by name from the HyperCore api and constructs
        object SnapshotSchedule if the record exists. If there is no record with such name, None is returned.
        """
        query = get_query(ansible_dict, "name", ansible_hypercore_map=dict(name="name"))
        hypercore_dict = rest_client.get_record(
            "/rest/v1/VirDomainSnapshotSchedule", query, must_exist=must_exist
        )
        snapshot_schedule_from_hypercore = SnapshotSchedule.from_hypercore(
            hypercore_dict
        )
        return snapshot_schedule_from_hypercore

    def create_post_payload(self):
        return self._post_and_patch_payload()

    def create_patch_payload(self, new_recurrences_ansible_list):
        # Override the existing Recurrence objects with the new ones.
        # Then construct the same payload as in create_post_payload.
        self.recurrences = [
            Recurrence.from_ansible(new_recurrence)
            for new_recurrence in new_recurrences_ansible_list
        ]
        return self._post_and_patch_payload()

    def _post_and_patch_payload(self):
        """Method shared by create_post_payload and create_patch_payload"""
        return dict(
            name=self.name,
            rrules=[
                recurrence.create_post_and_patch_payload()
                for recurrence in self.recurrences
            ],
        )


class Recurrence(PayloadMapper):
    # Variables in SnapshotSchedule are written in ansible-native format
    def __init__(
        self,
        name,
        frequency,
        start,
        local_retention,
        remote_retention=None,
        replication=True,
        uuid=None,
    ):
        self.name = name
        self.frequency = frequency
        self.start = start
        self.local_retention = local_retention
        self.remote_retention = remote_retention
        self.replication = replication
        self.uuid = uuid

    @classmethod
    def from_ansible(cls, vm_dict):
        if vm_dict.get("remote_retention", None):
            remote_retention = vm_dict["remote_retention"]
        else:
            remote_retention = vm_dict["local_retention"]
        return Recurrence(
            name=vm_dict["name"],
            frequency=vm_dict["frequency"],
            start=vm_dict["start"],
            local_retention=vm_dict["local_retention"],
            remote_retention=remote_retention,
        )

    @classmethod
    def from_hypercore(cls, vm_dict):
        if not vm_dict:  # In case for get_record, return None if no result is found
            return None
        return Recurrence(
            name=vm_dict["name"],
            frequency=vm_dict["rrule"],
            start=vm_dict["dtstart"],
            local_retention=vm_dict["localRetentionDurationSeconds"],
            remote_retention=vm_dict["remoteRetentionDurationSeconds"],
            replication=vm_dict["replication"],
            uuid=vm_dict["uuid"],
        )

    def to_hypercore(self):
        return dict(
            name=self.name,
            rrule=self.frequency,
            dtstart=self.start,
            localRetentionDurationSeconds=self.local_retention,
            remoteRetentionDurationSeconds=self.remote_retention,
            replication=self.replication,
            uuid=self.uuid,
        )

    def to_ansible(self):
        return dict(
            name=self.name,
            frequency=self.frequency,
            start=self.start,
            local_retention=self.local_retention,
            remote_retention=self.remote_retention,
            replication=self.replication,
            uuid=self.uuid,
        )

    def __eq__(self, other):
        """One SnapshotSchedule is equal to another if it has ALL attributes exactly the same"""
        # Used only in tests.
        return all(
            (
                self.name == other.name,
                self.frequency == other.frequency,
                self.start == other.start,
                self.local_retention == other.local_retention,
                self.remote_retention == other.remote_retention,
                self.replication == other.replication,
                self.uuid == other.uuid,
            )
        )

    def __str__(self):
        return super().__str__()

    def create_post_and_patch_payload(self):
        hypercore_payload_dict = self.to_hypercore()
        hypercore_payload_dict["replication"] = True
        del hypercore_payload_dict["uuid"]
        return hypercore_payload_dict
