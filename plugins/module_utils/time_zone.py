# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper, get_query
from ..module_utils import errors


# ------------------------------------------
# NOTES:
# - use HC3 API Settings as reference
#     - there you can change Time Zone
#         - it not be empty
#         - has to exist
#         - 0 or 1 of them (like DNS config)
#         - hardcoded uuid (like DNS config)
class TimeZone(PayloadMapper):
    def __init__(
        self,
        uuid: str = None,
        zone: str = None,
        latest_task_tag: {} = None,
    ):
        self.uuid = uuid
        self.zone = zone
        self.latest_task_tag = latest_task_tag

    @classmethod
    def from_ansible(cls, ansible_data):
        return TimeZone(
            uuid=ansible_data["uuid"],
            zone=ansible_data["timeZone"],
            latest_task_tag=ansible_data["latestTaskTag"],
        )

    @classmethod
    def from_hypercore(cls, hypercore_data):
        if not hypercore_data:
            return None

        return cls(
            uuid=hypercore_data["uuid"],
            zone=hypercore_data["timeZone"],
            latest_task_tag=hypercore_data["latestTaskTag"],
        )

    def to_hypercore(self) -> dict:
        return dict(
            uuid=self.uuid,
            timeZone=self.zone,
        )

    def to_ansible(self):
        return dict(
            uuid=self.uuid,
            zone=self.zone,
            latest_task_tag=self.latest_task_tag,
        )

    # This method is here for testing purposes!
    def __eq__(self, other):
        return all(
            (
                self.uuid == other.uuid,
                self.zone == other.zone,
                self.latest_task_tag == other.latest_task_tag,
            )
        )

    @classmethod
    def get_by_uuid(cls, ansible_dict, rest_client, must_exist=False):
        query = get_query(ansible_dict, "uuid", ansible_hypercore_map=dict(uuid="uuid"))
        hypercore_dict = rest_client.get_record(
            "/rest/v1/TimeZone", query, must_exist=must_exist
        )
        time_zone_from_hypercore = TimeZone.from_hypercore(hypercore_dict)
        return time_zone_from_hypercore

    @classmethod
    def get_state(cls, rest_client):
        state = [
            TimeZone.from_hypercore(hypercore_data=hypercore_dict).to_ansible()
            for hypercore_dict in rest_client.list_records("/rest/v1/TimeZone/")
        ]

        # Raise an error if there is more than 1 Time Zone in HyperCore API settings
        # - There should be 0 or 1 Time Zone available
        if len(state) > 1:
            raise errors.ScaleComputingError(
                "Time Zone: There are too many Time Zone entries!\n\
                The number of Time Zone entries should be 0 or 1."
            )
        if len(state) == 0:
            return {}
        return state[0]
