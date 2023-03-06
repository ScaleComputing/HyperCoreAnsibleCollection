# -*- coding: utf-8 -*-
# Copyright: (c) 2021, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

from . import errors
from . import utils
from ..module_utils.client import Client
from ..module_utils.typed_classes import TypedTaskTag

__metaclass__ = type

from typing import Any, Union


def _query(original=None):
    # Make sure the query isn't equal to None
    # If any default query values need to added in the future, they may be added here
    return dict(original or {})


class RestClient:
    def __init__(self, client: Client):
        self.client = client

    def list_records(
        self, endpoint: str, query: dict[Any, Any] = None, timeout: float = None
    ) -> list[Any]:
        """Results are obtained so that first off, all records are obtained and
        then filtered manually"""
        try:
            records = self.client.get(path=endpoint, timeout=timeout).json
        except TimeoutError as e:
            raise errors.ScaleComputingError(f"Request timed out: {e}")
        return utils.filter_results(records, query)

    def get_record(
        self,
        endpoint: str,
        query: dict[Any, Any] = None,
        must_exist: bool = False,
        timeout: float = None,
    ) -> Union[dict[Any, Any], None]:
        records = self.list_records(endpoint=endpoint, query=query, timeout=timeout)
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

    def create_record(
        self, endpoint, payload, check_mode, timeout=None
    ) -> TypedTaskTag:
        if check_mode:
            return utils.MOCKED_TASK_TAG
        try:
            response: TypedTaskTag = self.client.post(
                endpoint, payload, query=_query(), timeout=timeout
            ).json
        except TimeoutError as e:
            raise errors.ScaleComputingError(f"Request timed out: {e}")
        return response

    def update_record(
        self, endpoint, payload, check_mode, record=None, timeout=None
    ) -> TypedTaskTag:
        # No action is possible when updating a record
        if check_mode:
            return utils.MOCKED_TASK_TAG
        try:
            response: TypedTaskTag = self.client.patch(
                endpoint, payload, query=_query(), timeout=timeout
            ).json
        except TimeoutError as e:
            raise errors.ScaleComputingError(f"Request timed out: {e}")
        return response

    def delete_record(self, endpoint, check_mode, timeout=None) -> TypedTaskTag:
        # No action is possible when deleting a record
        if check_mode:
            return utils.MOCKED_TASK_TAG
        try:
            response: TypedTaskTag = self.client.delete(endpoint, timeout=timeout).json
        except TimeoutError as e:
            raise errors.ScaleComputingError(f"Request timed out: {e}")
        return response

    def put_record(
        self,
        endpoint: str,
        payload: Union[dict[Any, Any], None],
        check_mode: bool,
        query: Union[dict[Any, Any], None] = None,
        timeout: int = None,
        binary_data: bytes = None,
        headers=None,
    ) -> TypedTaskTag:
        # Method put doesn't support check mode # IT ACTUALLY DOES
        if check_mode:
            return utils.MOCKED_TASK_TAG
        try:
            response: TypedTaskTag = self.client.put(
                endpoint,
                data=payload,
                query=query,
                timeout=timeout,
                binary_data=binary_data,
                headers=headers,
            ).json
        except TimeoutError as e:
            raise errors.ScaleComputingError(f"Request timed out: {e}")
        return response


class CachedRestClient(RestClient):
    # Use ONLY in case, that all task operations are read only. Should hould for all _info
    # modules.

    def __init__(self, client: Client):
        super().__init__(client)
        self.cache = dict()

    def list_records(
        self, endpoint: str, query: dict[Any, Any] = None, timeout: float = None
    ) -> list[Any]:
        if endpoint in self.cache:
            records = self.cache[endpoint]
        else:
            try:
                records = self.client.get(path=endpoint, timeout=timeout).json
            except TimeoutError as e:
                raise errors.ScaleComputingError(f"Request timed out: {e}")
            self.cache[endpoint] = records

        return utils.filter_results(records, query)
