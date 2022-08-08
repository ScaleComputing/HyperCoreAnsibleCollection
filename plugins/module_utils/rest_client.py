# -*- coding: utf-8 -*-
# Copyright: (c) 2021, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

# import errors
from . import errors

__metaclass__ = type


def is_superset(superset, candidate):
    if not candidate:
        return True
    for k, v in candidate.items():
        if k in superset and superset[k] == v:
            continue
        return False
    return True


def filter_results(results, filter_data):
    return [element for element in results if is_superset(element, filter_data)]


def _query(original=None):
    # Make sure the query isn't equal to None
    # If any default query values need to added in the future, they may be added here
    return dict(original or {})


class RestClient:
    def __init__(self, client):
        self.client = client

    def list_records(self, endpoint, query=None):
        """Results are obtained so that first off, all records are obtained and
        then filtered manually"""
        records = self.client.get(path=endpoint).json
        return filter_results(records, query)

    def get_record(self, endpoint, query=None, must_exist=False):
        records = self.list_records(endpoint=endpoint, query=query)
        if len(records) > 1:
            raise errors.ScaleComputingError(
                "{0} records from endpoint {1} match the {2} query.".format(
                    len(records), endpoint, query
                )
            )
        if must_exist and not records:
            raise errors.ScaleComputingError(
                "No records from endpoint {0} match the {1} query.".format(
                    endpoint, query
                )
            )
        return records[0] if records else None

    def create_record(self, endpoint, payload, check_mode):
        if check_mode:
            # Approximate the result using the payload.
            return payload
        return self.client.post(endpoint, payload, query=_query()).json

    def update_record(self, endpoint, payload, check_mode, record=None):
        # No action is possible when updating a record
        if check_mode:
            # Approximate the result by manually patching the existing state.
            return dict(record or {}, **payload)
        return self.client.patch(endpoint, payload, query=_query()).json

    def delete_record(self, endpoint, check_mode):
        # No action is possible when deleting a record
        if check_mode:
            return
        self.client.delete(endpoint)
