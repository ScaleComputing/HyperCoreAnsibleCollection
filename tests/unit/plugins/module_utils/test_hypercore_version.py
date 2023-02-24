# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.hypercore_version import (
    HyperCoreVersion,
    Version,
    VersionSpecSimple,
    VersionSpec,
    Update,
    UpdateStatus,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestHyperCoreVersion:
    def test_simple(self):
        hcversion = HyperCoreVersion(None)
        hcversion._version = "9.1.10.2345"
        assert hcversion.verify(">1.2.3") is True

        assert hcversion.verify("==9.1.10") is True
        assert hcversion.verify(">=9.1.10") is True
        assert hcversion.verify(">9.1.10") is False

        assert hcversion.verify("<9.2.0") is True
        assert hcversion.verify(">9.2.0") is False
        assert hcversion.verify(">=9.2.0") is False
        assert hcversion.verify(">=9.2.0") is False

        assert hcversion.verify("<9.2.10") is True
        assert hcversion.verify(">9.2.10") is False
        assert hcversion.verify(">=9.2.10") is False
        assert hcversion.verify(">=9.2.10") is False

    @pytest.mark.parametrize(
        ("version", "expected_result"),
        [
            ["8.9.10.2345", False],
            ["9.0.10.2345", False],
            ["9.1.8.2345", False],
            ["9.1.9.2345", True],
            ["9.1.10.2345", True],
            ["9.2.9.2345", False],
            ["9.2.10.2345", True],
            ["9.2.11.2345", True],
        ],
    )
    def test_compound(self, version, expected_result):
        # needed feature was added in 9.2.10 and backported to 9.1.9.
        hcversion = HyperCoreVersion(None)
        hcversion._version = version
        assert hcversion.verify(">=9.1.9 <9.2.0 || >=9.2.10") is expected_result


class TestVersion:
    def test_parts(self):
        version_str = "8.9.10"
        version = Version(version_str)
        assert [8, 9, 10] == version.parts

    @pytest.mark.parametrize(
        ("v1", "v2", "expected_result"),
        [
            # change 1st part
            ["8.9.10", "7.9.10", False],
            ["8.9.10", "8.9.10", False],
            ["8.9.10", "9.9.10", True],
            # change 2nd part
            ["8.9.10", "8.8.10", False],
            ["8.9.10", "8.9.10", False],
            ["8.9.10", "8.10.10", True],
            # change 3rd part
            ["8.9.10", "8.9.9", False],
            ["8.9.10", "8.9.10", False],
            ["8.9.10", "8.9.11", True],
        ],
    )
    def test_lt(self, v1, v2, expected_result):
        assert expected_result == (Version(v1) < Version(v2))


class TestVersionSpecSimple:
    @pytest.mark.parametrize(
        ("version_str", "spec_str", "expected_result"),
        [
            # lt
            ["9.5.2", "<9.0.10", False],
            ["9.5.2", "<9.4.10", False],
            ["9.5.2", "<9.5.1", False],
            ["9.5.2", "<9.5.2", False],
            ["9.5.2", "<9.5.3", True],
            ["9.5.2", "<9.6.0", True],
            ["9.5.2", "<10.6.0", True],
            # le
            ["9.5.2", "<=9.0.10", False],
            ["9.5.2", "<=9.4.10", False],
            ["9.5.2", "<=9.5.1", False],
            ["9.5.2", "<=9.5.2", True],
            ["9.5.2", "<=9.5.3", True],
            ["9.5.2", "<=9.6.0", True],
            ["9.5.2", "<=10.6.0", True],
            # gt
            ["9.5.2", ">9.0.10", True],
            ["9.5.2", ">9.4.10", True],
            ["9.5.2", ">9.5.1", True],
            ["9.5.2", ">9.5.2", False],
            ["9.5.2", ">9.5.3", False],
            ["9.5.2", ">9.6.0", False],
            ["9.5.2", ">10.6.0", False],
            # ge
            ["9.5.2", ">=9.0.10", True],
            ["9.5.2", ">=9.4.10", True],
            ["9.5.2", ">=9.5.1", True],
            ["9.5.2", ">=9.5.2", True],
            ["9.5.2", ">=9.5.3", False],
            ["9.5.2", ">=9.6.0", False],
            ["9.5.2", ">=10.6.0", False],
            # eq
            ["9.5.2", "==9.0.10", False],
            ["9.5.2", "==9.4.10", False],
            ["9.5.2", "==9.5.1", False],
            ["9.5.2", "==9.5.2", True],
            ["9.5.2", "==9.5.3", False],
            ["9.5.2", "==9.6.0", False],
            ["9.5.2", "==10.6.0", False],
        ],
    )
    def test_match(self, version_str, spec_str, expected_result):
        version = Version(version_str)
        spec = VersionSpecSimple(spec_str)
        assert spec.match(version) is expected_result


class TestVersionSpec:
    @pytest.mark.parametrize(
        ("version_str", "spec_str", "expected_result"),
        [
            ["9.0.10", ">=9.1.9 <9.2.0 || >=9.2.10", False],
            ["9.1.0", ">=9.1.9 <9.2.0 || >=9.2.10", False],
            ["9.1.8", ">=9.1.9 <9.2.0 || >=9.2.10", False],
            ["9.1.9", ">=9.1.9 <9.2.0 || >=9.2.10", True],
            ["9.1.10", ">=9.1.9 <9.2.0 || >=9.2.10", True],
            ["9.2.0", ">=9.1.9 <9.2.0 || >=9.2.10", False],
            ["9.2.1", ">=9.1.9 <9.2.0 || >=9.2.10", False],
            ["9.2.9", ">=9.1.9 <9.2.0 || >=9.2.10", False],
            ["9.2.10", ">=9.1.9 <9.2.0 || >=9.2.10", True],
            ["9.2.11", ">=9.1.9 <9.2.0 || >=9.2.10", True],
            ["9.3.0", ">=9.1.9 <9.2.0 || >=9.2.10", True],
        ],
    )
    def test_match(self, version_str, spec_str, expected_result):
        # no special constraint means it is OK
        spec = VersionSpec(spec_str)
        version = Version(version_str)
        assert spec.match(version) is expected_result


class TestUpdate:
    def test_update_from_hypercore_dict_not_empty(self):
        update = Update(
            uuid="9.2.11.210763",
            description="description",
            change_log="change log",
            build_id=210763,
            major_version=9,
            minor_version=2,
            revision=11,
            timestamp=1676920067,
        )
        hypercore_dict = dict(
            uuid="9.2.11.210763",
            description="description",
            changeLog="change log",
            buildID=210763,
            majorVersion=9,
            minorVersion=2,
            revision=11,
            timestamp=1676920067,
        )

        update_from_hypercore = Update.from_hypercore(hypercore_dict)
        assert update == update_from_hypercore

    def test_update_from_hypercore_dict_empty(self):
        assert Update.from_hypercore([]) is None

    def test_update_to_ansible(self):
        update = Update(
            uuid="9.2.11.210763",
            description="description",
            change_log="change log",
            build_id=210763,
            major_version=9,
            minor_version=2,
            revision=11,
            timestamp=1676920067,
        )

        ansible_dict = dict(
            uuid="9.2.11.210763",
            description="description",
            change_log="change log",
            build_id=210763,
            major_version=9,
            minor_version=2,
            revision=11,
            timestamp=1676920067,
        )

        assert update.to_ansible() == ansible_dict

    def test_update_equal_true(self):
        update1 = Update(
            uuid="9.2.11.210763",
            description="description",
            change_log="change log",
            build_id=210763,
            major_version=9,
            minor_version=2,
            revision=11,
            timestamp=1676920067,
        )
        update2 = Update(
            uuid="9.2.11.210763",
            description="description",
            change_log="change log",
            build_id=210763,
            major_version=9,
            minor_version=2,
            revision=11,
            timestamp=1676920067,
        )

        assert update1 == update2

    def test_update_equal_false(self):
        update1 = Update(
            uuid="10.2.11.210763",
            description="description",
            change_log="change log",
            build_id=210763,
            major_version=10,
            minor_version=2,
            revision=11,
            timestamp=1676920067,
        )
        update2 = Update(
            uuid="9.2.11.210763",
            description="description",
            change_log="change log",
            build_id=210763,
            major_version=9,
            minor_version=2,
            revision=11,
            timestamp=1676920067,
        )

        assert update1 != update2

    def test_apply_update(self, rest_client):
        icos_version = "9.2.11.210763"

        Update.apply_update(rest_client, icos_version)

        rest_client.create_record.assert_called_with(
            f"/rest/v1/Update/{icos_version}/apply",
            {},
            False,
        )


class TestUpdateStatus:
    def test_update_status_from_hypercore(self):
        update_status = UpdateStatus(
            from_build="207183",
            percent="100",
            status="COMPLETE",
            status_details="Update Complete. Press 'Reload' to reconnect",
            to_build="209840",
            to_version="9.1.18.209840",
        )
        hypercore_dict = dict(
            prepareStatus="",
            updateStatus=dict(
                masterStateID="4",
                masterState="COMPLETE",
                fromBuild="207183",
                toBuild="209840",
                toVersion="9.1.18.209840",
                currentComponent="2075",
                totalComponents="2075",
                percent="100",
                status=dict(
                    component="7540/9999",
                    node="173.16.93.134",
                    statusdetails="Update Complete. Press 'Reload' to reconnect",
                    usernotes="Update Complete. Press 'Reload' to reconnect",
                ),
            ),
        )

        update_status_from_hypercore = UpdateStatus.from_hypercore(hypercore_dict)
        assert update_status == update_status_from_hypercore

    def test_update_status_to_ansible(self):
        update_status = UpdateStatus(
            from_build="207183",
            percent="100",
            status="COMPLETE",
            status_details="Update Complete. Press 'Reload' to reconnect",
            to_build="209840",
            to_version="9.1.18.209840",
        )
        ansible_dict = dict(
            from_build="207183",
            percent="100",
            status="COMPLETE",
            status_details="Update Complete. Press 'Reload' to reconnect",
            to_build="209840",
            to_version="9.1.18.209840",
        )

        assert update_status.to_ansible() == ansible_dict
