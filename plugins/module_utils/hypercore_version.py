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
from ..module_utils.utils import PayloadMapper
from ..module_utils.rest_client import RestClient
from ..module_utils.typed_classes import (
    TypedUpdateToAnsible,
    TypedUpdateStatusToAnsible,
    TypedTaskTag,
)
from typing import Any, Union


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


class Update(PayloadMapper):
    def __init__(
        self,
        uuid: str,
        description: str,
        change_log: str,
        build_id: int,
        major_version: int,
        minor_version: int,
        revision: int,
        timestamp: int,
    ):
        self.uuid = uuid
        self.description = description
        self.change_log = change_log
        self.build_id = build_id
        self.major_version = major_version
        self.minor_version = minor_version
        self.revision = revision
        self.timestamp = timestamp

    @classmethod
    def from_ansible(cls, ansible_data: dict[Any, Any]) -> None:
        pass

    @classmethod
    def from_hypercore(cls, hypercore_data: dict[Any, Any]) -> Union[Update, None]:
        if not hypercore_data:
            return None
        return cls(
            uuid=hypercore_data["uuid"],
            description=hypercore_data["description"],
            change_log=hypercore_data["changeLog"],
            build_id=hypercore_data["buildID"],
            major_version=hypercore_data["majorVersion"],
            minor_version=hypercore_data["minorVersion"],
            revision=hypercore_data["revision"],
            timestamp=hypercore_data["timestamp"],
        )

    def to_hypercore(self) -> None:
        pass

    def to_ansible(self) -> TypedUpdateToAnsible:
        return dict(
            uuid=self.uuid,
            description=self.description,
            change_log=self.change_log,
            build_id=self.build_id,
            major_version=self.major_version,
            minor_version=self.minor_version,
            revision=self.revision,
            timestamp=self.timestamp,
        )

    def __eq__(self, other: object) -> bool:
        """
        One Update is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        if not isinstance(other, Update):
            return NotImplemented
        return all(
            (
                self.uuid == other.uuid,
                self.description == other.description,
                self.change_log == other.change_log,
                self.build_id == other.build_id,
                self.major_version == other.major_version,
                self.minor_version == other.minor_version,
                self.revision == other.revision,
                self.timestamp == other.timestamp,
            )
        )

    @staticmethod
    def apply(
        rest_client: RestClient, icos_version: str, check_mode: bool = False
    ) -> TypedTaskTag:
        return rest_client.create_record(
            f"/rest/v1/Update/{icos_version}/apply", dict(), check_mode
        )


class UpdateStatus(PayloadMapper):
    def __init__(
        self,
        status: str,
        from_build: str,
        to_build: str,
        to_version: str,
        percent: str,
        status_details: str,
    ):
        self.status = status
        self.from_build = from_build
        self.to_build = to_build
        self.to_version = to_version
        self.percent = percent
        self.status_details = status_details

    @classmethod
    def from_ansible(cls, ansible_data: dict[Any, Any]) -> None:
        pass

    @classmethod
    def from_hypercore(cls, hypercore_data: dict[Any, Any]) -> UpdateStatus:
        return cls(
            status=hypercore_data["updateStatus"]["masterState"],
            from_build=hypercore_data["updateStatus"]["fromBuild"],
            to_build=hypercore_data["updateStatus"]["toBuild"],
            to_version=hypercore_data["updateStatus"]["toVersion"],
            percent=hypercore_data["updateStatus"]["percent"],
            status_details=hypercore_data["updateStatus"]["status"]["statusdetails"],
        )

    def to_hypercore(self) -> None:
        pass

    def to_ansible(self) -> TypedUpdateStatusToAnsible:
        return dict(
            status=self.status,
            from_build=self.from_build,
            to_build=self.to_build,
            to_version=self.to_version,
            percent=self.percent,
            status_details=self.status_details,
        )

    def __eq__(self, other: object) -> bool:
        """
        One UpdateStatus is equal to another if it has ALL attributes exactly the same.
        This method is used only in tests.
        """
        if not isinstance(other, UpdateStatus):
            return NotImplemented
        return all(
            (
                self.status == other.status,
                self.from_build == other.from_build,
                self.to_build == other.to_build,
                self.to_version == other.to_version,
                self.percent == other.percent,
                self.status_details == other.status_details,
            )
        )

    @classmethod
    def get(cls, rest_client: RestClient, check_mode: bool = False) -> UpdateStatus:
        update_status = rest_client.client.get("update/update_status.json").json  # type: ignore
        return cls.from_hypercore(update_status)
