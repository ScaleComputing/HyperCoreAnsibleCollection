# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

import operator
import re
from functools import total_ordering
from typing import List
from .rest_client import RestClient


class HyperCoreVersion:
    """
    Check if HyperCore version does support required feature.
    Examples include:
    - VirtualDisk endpoint
    - PATCH for cluster name
    """

    def __init__(self, rest_client: RestClient):
        self._rest_client = rest_client
        self._version = ""

    @property
    def version(self) -> str:
        if not self._version:
            record = self._rest_client.get_record("/rest/v1/Cluster")
            if (
                record is None
                or "icosVersion" not in record
                or not isinstance(record["icosVersion"], str)
            ):
                raise AssertionError(
                    "HyperCore version not found in REST API response."
                )
            self._version = record["icosVersion"]
        return self._version

    def verify(self, spec: str) -> bool:
        # Use spec ">=9.1.9 <9.2.0 || >=9.2.10" to detect a feature
        # added in 9.2.10 and backported to 9.1.9.
        version = self.version
        version = ".".join(version.split(".")[:3])
        return VersionSpec(spec).match(Version(version))


@total_ordering
class Version:
    def __init__(self, version: str):
        self.version = version.strip()
        if not re.match(r"^[.0-9]*$", self.version):
            raise AssertionError()
        # work only with semver-like versions - "a.b.c"
        if self.version.count(".") != 2:
            raise AssertionError()

    @property
    def parts(self) -> List[int]:
        parts_str = self.version.split(".")
        parts = [int(pp) for pp in parts_str]
        return parts

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        my_parts = self.parts
        other_parts = other.parts
        for my_part, other_part in zip(my_parts, other_parts):
            if my_part < other_part:
                return True
            elif my_part > other_part:
                return False
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts


class VersionSpecBase:
    def __init__(self, spec: str):
        raise NotImplementedError()

    def match(self, version: Version) -> bool:
        raise NotImplementedError()


class VersionSpecSimple(VersionSpecBase):
    def __init__(self, spec: str):
        """
        :param spec:
        Must be "operator + version". NO space between!.
        operator: <, <=, >, >=, ==.
        """
        self.spec = spec.strip()
        if " " in self.spec:
            raise AssertionError()
        re_match = re.search(r"[^<>=]", self.spec)
        if re_match is None:
            raise AssertionError()
        version_ind = re_match.start()
        operator_str = self.spec[:version_ind]
        version = self.spec[version_ind:]
        self._version = Version(version)
        operator_map = {
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
            "==": operator.eq,
        }
        self._operator = operator_map[operator_str]

    def match(self, version: Version) -> bool:
        return bool(self._operator(version, self._version))


class VersionSpec(VersionSpecBase):
    def __init__(self, spec: str):
        self.spec = spec.strip()
        self._childs: List[VersionSpecBase]
        if "||" in self.spec:
            self._operator = any
            subspecs_str = self.spec.split("||")
            self._childs = [VersionSpec(subspec.strip()) for subspec in subspecs_str]
        else:
            self._operator = all
            subspecs_str = self.spec.split()
            self._childs = [VersionSpecSimple(subspec) for subspec in subspecs_str]

    def match(self, version: Version) -> bool:
        results = [child.match(version) for child in self._childs]
        return self._operator(results)
