# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

import json
from typing import Any, Optional, Union

from ansible.module_utils.urls import Request, basic_auth_header

from .errors import AuthError, ScaleComputingError, UnexpectedAPIResponse
from ..module_utils.typed_classes import TypedClusterInstance

from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote

DEFAULT_HEADERS = dict(Accept="application/json")


class Response:
    # I have felling (but I'm not sure) we will always use
    # "Response(raw_resp.status, raw_resp.read(), raw_resp.headers)"
    # Response(raw_resp) would be simpler.
    # How is this used in other projects? Jure?
    # Maybe we need/want both.
    def __init__(
        self, status: int, data: Any, headers: Optional[dict[Any, Any]] = None
    ):
        self.status = status
        self.data = data
        # [('h1', 'v1'), ('H2', 'V2')] -> {'h1': 'v1', 'h2': 'V2'}
        self.headers = (
            dict((k.lower(), v) for k, v in dict(headers).items()) if headers else {}
        )

        self._json = None

    @property
    def json(self) -> Any:
        if self._json is None:
            try:
                self._json = json.loads(self.data)
            except ValueError:
                raise ScaleComputingError(
                    "Received invalid JSON response: {0}".format(self.data)
                )
        return self._json


class Client:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        timeout: float,
    ):
        if not (host or "").startswith(("https://", "http://")):
            raise ScaleComputingError(
                "Invalid instance host value: '{0}'. "
                "Value must start with 'https://' or 'http://'".format(host)
            )

        self.host = host
        self.username = username
        self.password = password
        self.timeout = timeout

        self._auth_header: Optional[dict[str, bytes]] = None
        self._client = Request()

    @classmethod
    def get_client(cls, cluster_instance: TypedClusterInstance) -> Client:
        return cls(
            cluster_instance["host"],
            cluster_instance["username"],
            cluster_instance["password"],
            cluster_instance["timeout"],
        )

    @property
    def auth_header(self) -> dict[str, bytes]:
        if not self._auth_header:
            self._auth_header = self._login()
        return self._auth_header

    def _login(self) -> dict[str, bytes]:
        return self._login_username_password()

    def _login_username_password(self) -> dict[str, bytes]:
        return dict(Authorization=basic_auth_header(self.username, self.password))

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Union[dict[Any, Any], bytes, str]] = None,
        headers: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Response:
        if (
            timeout is None
        ):  # If timeout from request is not specifically provided, take it from the Client.
            timeout = self.timeout
        try:
            raw_resp = self._client.open(
                method,
                path,
                data=data,
                headers=headers,
                validate_certs=False,
                timeout=timeout,
            )
        except HTTPError as e:
            # Wrong username/password, or expired access token
            if e.code == 401:
                raise AuthError(
                    "Failed to authenticate with the instance: {0} {1}".format(
                        e.code, e.reason
                    ),
                )
            # Other HTTP error codes do not necessarily mean errors.
            # This is for the caller to decide.
            return Response(e.code, e.read(), e.headers)
        except URLError as e:
            # TODO: Add other errors here; we need to handle them in modules.
            if (
                e.args
                and isinstance(e.args, tuple)
                and type(e.args[0]) == ConnectionRefusedError
            ):
                raise ConnectionRefusedError(
                    e.reason
                )
            elif (
                e.args
                and isinstance(e.args, tuple)
                and type(e.args[0]) == ConnectionResetError
            ):
                raise ConnectionResetError(e.reason)
            raise ScaleComputingError(e.reason)
        return Response(raw_resp.status, raw_resp.read(), raw_resp.headers)

    def request(
        self,
        method: str,
        path: str,
        query: Optional[dict[Any, Any]] = None,
        data: Optional[dict[Any, Any]] = None,
        headers: Optional[dict[Any, Any]] = None,
        binary_data: Optional[bytes] = None,
        timeout: Optional[float] = None,
    ) -> Response:
        # Make sure we only have one kind of payload
        if data is not None and binary_data is not None:
            raise AssertionError(
                "Cannot have JSON and binary payload in a single request."
            )
        escaped_path = quote(path.strip("/"))
        if escaped_path:
            escaped_path = "/" + escaped_path
        url = "{0}{1}".format(self.host, escaped_path)
        if query:
            url = "{0}?{1}".format(url, urlencode(query))
        headers = dict(headers or DEFAULT_HEADERS, **self.auth_header)
        if data is not None:
            headers["Content-type"] = "application/json"
            return self._request(
                method,
                url,
                data=json.dumps(data, separators=(",", ":")),
                headers=headers,
                timeout=timeout,
            )
        elif binary_data is not None:
            headers["Content-type"] = "application/octet-stream"
            return self._request(
                method, url, data=binary_data, headers=headers, timeout=timeout
            )
        return self._request(method, url, data=data, headers=headers, timeout=timeout)

    def get(
        self,
        path: str,
        query: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Request:
        resp = self.request("GET", path, query=query, timeout=timeout)
        if resp.status in (200, 404):
            return resp
        raise UnexpectedAPIResponse(response=resp)

    def post(
        self,
        path: str,
        data: Optional[dict[Any, Any]],
        query: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Request:
        resp = self.request("POST", path, data=data, query=query, timeout=timeout)
        if resp.status == 201 or resp.status == 200:
            return resp
        raise UnexpectedAPIResponse(response=resp)

    def patch(
        self,
        path: str,
        data: dict[Any, Any],
        query: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Request:
        resp = self.request("PATCH", path, data=data, query=query, timeout=timeout)
        if resp.status == 200:
            return resp
        raise UnexpectedAPIResponse(response=resp)

    def put(
        self,
        path: str,
        data: Optional[dict[Any, Any]],
        query: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
        binary_data: Optional[bytes] = None,
        headers: Optional[dict[Any, Any]] = None,
    ) -> Request:
        resp = self.request(
            "PUT",
            path,
            data=data,
            query=query,
            timeout=timeout,
            binary_data=binary_data,
            headers=headers,
        )
        if resp.status == 200:
            return resp
        raise UnexpectedAPIResponse(response=resp)

    def delete(
        self,
        path: str,
        query: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Request:
        resp = self.request("DELETE", path, query=query, timeout=timeout)
        if resp.status == 204 or resp.status == 200:
            return resp
        raise UnexpectedAPIResponse(response=resp)
