# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible.module_utils.urls import Request, basic_auth_header

from .errors import AuthError, ScaleComputingError, UnexpectedAPIResponse

from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote

DEFAULT_HEADERS = dict(Accept="application/json")


class Response:
    # I have felling (but I'm not sure) we will always use
    # "Response(raw_resp.status, raw_resp.read(), raw_resp.headers)"
    # Response(raw_resp) would be simpler.
    # How is this used in other projects? Jure?
    # Maybe we need/want both.
    def __init__(self, status, data, headers=None):
        self.status = status
        self.data = data
        # [('h1', 'v1'), ('H2', 'V2')] -> {'h1': 'v1', 'h2': 'V2'}
        self.headers = (
            dict((k.lower(), v) for k, v in dict(headers).items()) if headers else {}
        )

        self._json = None

    @property
    def json(self):
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

        self._auth_header = None
        self._client = Request()

    @classmethod
    def get_client(cls, cluster_instance: dict):
        return cls(
            cluster_instance["host"],
            cluster_instance["username"],
            cluster_instance["password"],
            cluster_instance["timeout"],
        )

    @property
    def auth_header(self):
        if not self._auth_header:
            self._auth_header = self._login()
        return self._auth_header

    def _login(self):
        return self._login_username_password()

    def _login_username_password(self):
        return dict(Authorization=basic_auth_header(self.username, self.password))

    def _request(self, method, path, data=None, headers=None, timeout=None):
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
            raise ScaleComputingError(e.reason)
        return Response(raw_resp.status, raw_resp.read(), raw_resp.headers)

    def request(
        self,
        method,
        path,
        query=None,
        data=None,
        headers=None,
        binary_data=None,
        timeout=None,
    ):
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
            data = json.dumps(data, separators=(",", ":"))
            headers["Content-type"] = "application/json"
        elif binary_data is not None:
            data = binary_data
        return self._request(method, url, data=data, headers=headers, timeout=timeout)

    def get(self, path, query=None, timeout=None):
        resp = self.request("GET", path, query=query, timeout=timeout)
        if resp.status in (200, 404):
            return resp
        raise UnexpectedAPIResponse(response=resp)

    def post(self, path, data, query=None, timeout=None):
        resp = self.request("POST", path, data=data, query=query, timeout=timeout)
        if resp.status == 201 or resp.status == 200:
            return resp
        raise UnexpectedAPIResponse(response=resp)

    def patch(self, path, data, query=None, timeout=None):
        resp = self.request("PATCH", path, data=data, query=query, timeout=timeout)
        if resp.status == 200:
            return resp
        raise UnexpectedAPIResponse(response=resp)

    def put(self, path, data, query=None, timeout=None, binary_data=None, headers=None):
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

    def delete(self, path, query=None, timeout=None):
        resp = self.request("DELETE", path, query=query, timeout=timeout)
        if resp.status == 204 or resp.status == 200:
            return resp
        raise UnexpectedAPIResponse(response=resp)
