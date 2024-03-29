# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

import json
import os
import ssl
from typing import Any, Optional, Union
from io import BufferedReader
import enum

from ansible.module_utils.urls import Request

from .errors import (
    AuthError,
    ScaleComputingError,
    UnexpectedAPIResponse,
    ApiResponseNotJson,
)
from ..module_utils.typed_classes import TypedClusterInstance

from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote

DEFAULT_HEADERS = dict(Accept="application/json")


def _str_to_bool(s: str) -> bool:
    return s.lower() not in ["", "0", "false", "f", "no", "n"]


SC_DEBUG_LOG_TRAFFIC = _str_to_bool(os.environ.get("SC_DEBUG_LOG_TRAFFIC", "0"))
if SC_DEBUG_LOG_TRAFFIC:
    try:
        import q as q_log  # type: ignore
    except ImportError:
        # a do-nothing replacement
        def q_log(*args, **kwargs):  # type: ignore
            pass


class AuthMethod(str, enum.Enum):
    local = "local"
    oidc = "oidc"


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
                raise ApiResponseNotJson(self.data)
        return self._json


class Client:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        timeout: float,
        auth_method: str,
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
        self.auth_method = auth_method

        self._auth_header: Optional[dict[str, str]] = None
        self._client = Request()

    @classmethod
    def get_client(cls, cluster_instance: TypedClusterInstance) -> Client:
        return cls(
            cluster_instance["host"],
            cluster_instance["username"],
            cluster_instance["password"],
            cluster_instance["timeout"],
            cluster_instance["auth_method"],
        )

    @property
    def auth_header(self) -> dict[str, str]:
        if not self._auth_header:
            self._auth_header = self._login()
        return self._auth_header

    def _login(self) -> dict[str, str]:
        return self._login_username_password()

    def _login_username_password(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
        }
        use_oidc = self.auth_method == AuthMethod.oidc.value
        resp = self._request(
            "POST",
            f"{self.host}/rest/v1/login",
            data=json.dumps(
                dict(
                    username=self.username,
                    password=self.password,
                    useOIDC=use_oidc,
                )
            ),
            headers=headers,
            timeout=self.timeout,
        )
        return dict(Cookie=f"sessionID={resp.json['sessionID']}")

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Union[dict[Any, Any], bytes, str, BufferedReader]] = None,
        headers: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Response:
        # _request() with debug logging
        try:
            if SC_DEBUG_LOG_TRAFFIC:
                effective_timeout = timeout
                if timeout is None:
                    # If timeout from request is not specifically provided, take it from the Client.
                    effective_timeout = self.timeout
                request_in = dict(
                    method=method,
                    path=path,
                    data=data,
                    headers=headers,
                    timeout=effective_timeout,
                )
            resp = self._request_no_log(method, path, data, headers, timeout)
            if SC_DEBUG_LOG_TRAFFIC:
                request_out = dict(
                    status=resp.status,
                    data=resp.data,
                    headers=resp.headers,
                )
                q_log(request_in, request_out)
            return resp
        except Exception as exception:
            if SC_DEBUG_LOG_TRAFFIC:
                q_log(request_in, exception)
            raise

    def _request_no_log(
        self,
        method: str,
        path: str,
        data: Optional[Union[dict[Any, Any], bytes, str, BufferedReader]] = None,
        headers: Optional[dict[Any, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Response:
        if timeout is None:
            # If timeout from request is not specifically provided, take it from the Client.
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
            # TimeoutError is handled in the rest_client
            if (
                e.args
                and isinstance(e.args, tuple)
                and isinstance(e.args[0], ConnectionRefusedError)
            ):
                raise ConnectionRefusedError(e.reason)
            elif (
                e.args
                and isinstance(e.args, tuple)
                and isinstance(e.args[0], ConnectionResetError)
            ):
                raise ConnectionResetError(e.reason)
            elif (
                e.args
                and isinstance(e.args, tuple)
                and type(e.args[0])
                in [ssl.SSLEOFError, ssl.SSLZeroReturnError, ssl.SSLSyscallError]
            ):
                raise type(e.args[0])(e)
            raise ScaleComputingError(e.reason)
        return Response(raw_resp.status, raw_resp.read(), raw_resp.headers)

    def request(
        self,
        method: str,
        path: str,
        query: Optional[dict[Any, Any]] = None,
        data: Optional[dict[Any, Any]] = None,
        headers: Optional[dict[Any, Any]] = None,
        binary_data: Optional[Union[bytes, BufferedReader]] = None,
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
        binary_data: Optional[Union[bytes, BufferedReader]] = None,
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
