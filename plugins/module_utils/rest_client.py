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

from typing import Any, Optional, Union
from io import BufferedReader
import json


def _query(original: Optional[dict[Any, Any]] = None) -> dict[Any, Any]:
    # Make sure the query isn't equal to None
    # If any default query values need to added in the future, they may be added here
    return dict(original or {})


class RestClient:
    def __init__(self, client: Client):
        self.client = client

    def list_records(
        self,
        endpoint: str,
        query: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> list[Any]:
        """Results are obtained so that first off, all records are obtained and
        then filtered manually"""
        try:
            records = self.client.get(path=endpoint, timeout=timeout).json
        except TimeoutError as e:
            raise errors.ScaleTimeoutError(e)
        return utils.filter_results(records, query)

    def list_records_raw(
        self,
        endpoint: str,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Returns all records. No filtering is done.
        Returned type is same as type returned by HyperCore API.
        """
        try:
            records = self.client.get(path=endpoint, timeout=timeout).json
        except TimeoutError as e:
            raise errors.ScaleTimeoutError(e)
        return records

    def get_record(
        self,
        endpoint: str,
        query: Optional[dict[Any, Any]] = None,
        must_exist: bool = False,
        timeout: Optional[float] = None,
    ) -> Optional[dict[Any, Any]]:
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
        self,
        endpoint: str,
        payload: Optional[dict[Any, Any]],
        check_mode: bool,
        timeout: Optional[float] = None,
    ) -> TypedTaskTag:
        if check_mode:
            return utils.MOCKED_TASK_TAG
        try:
            response: TypedTaskTag = self.client.post(
                endpoint, payload, query=_query(), timeout=timeout
            ).json
        except TimeoutError as e:
            raise errors.ScaleTimeoutError(e)
        return response

    def update_record(
        self,
        endpoint: str,
        payload: dict[Any, Any],
        check_mode: bool,
        timeout: Optional[float] = None,
    ) -> TypedTaskTag:
        # No action is possible when updating a record
        if check_mode:
            return utils.MOCKED_TASK_TAG
        try:
            response: TypedTaskTag = self.client.patch(
                endpoint, payload, query=_query(), timeout=timeout
            ).json
        except TimeoutError as e:
            raise errors.ScaleTimeoutError(e)
        return response

    def delete_record(
        self, endpoint: str, check_mode: bool, timeout: Optional[float] = None
    ) -> TypedTaskTag:
        # No action is possible when deleting a record
        if check_mode:
            return utils.MOCKED_TASK_TAG
        try:
            response: TypedTaskTag = self.client.delete(endpoint, timeout=timeout).json
        except TimeoutError as e:
            raise errors.ScaleTimeoutError(e)
        return response

    def put_record(
        self,
        endpoint: str,
        payload: Optional[dict[Any, Any]],
        check_mode: bool,
        query: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
        binary_data: Optional[Union[bytes, BufferedReader]] = None,
        headers: Optional[dict[Any, Any]] = None,
    ) -> TypedTaskTag:
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
            raise errors.ScaleTimeoutError(e)
        except (json.JSONDecodeError, json.decoder.JSONDecodeError) as e:
            raise json.JSONDecodeError(e.msg, e.doc, e.pos)
        return response


class CachedRestClient(RestClient):
    # Use ONLY in case, that all task operations are read only. Should hould for all _info
    # modules.

    def __init__(self, client: Client):
        super().__init__(client)
        self.cache: dict[Any, Any] = dict()

    def list_records(
        self,
        endpoint: str,
        query: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> list[Any]:
        if endpoint in self.cache:
            records = self.cache[endpoint]
        else:
            try:
                records = self.client.get(path=endpoint, timeout=timeout).json
            except TimeoutError as e:
                raise errors.ScaleTimeoutError(e)
            self.cache[endpoint] = records

        return utils.filter_results(records, query)
