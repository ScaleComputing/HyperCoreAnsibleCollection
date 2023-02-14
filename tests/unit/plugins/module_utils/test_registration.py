# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.registration import (
    Registration,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestGet:
    def test_get_when_registration_not_exist(self, rest_client) -> None:
        rest_client.list_records.return_value = []
        result = Registration.get(rest_client)
        assert result is None

    def test_get_when_registration_exist(self, rest_client) -> None:
        rest_client.list_records.return_value = [
            dict(
                uuid="id",
                companyName="name",
                contact="contact",
                email="email",
                phone="phone",
                clusterID="id",
                clusterData="data",
                clusterDataHash="hash",
                clusterDataHashAccepted="hash_accepted",
            )
        ]
        result = Registration.get(rest_client)
        assert isinstance(result, Registration) is True
        assert result.uuid == "id"
        assert result.company_name == "name"
        assert result.contact == "contact"
        assert result.email == "email"
        assert result.phone == "phone"
        assert result.cluster_id == "id"
        assert result.cluster_data == "data"
        assert result.cluster_data_hash == "hash"
        assert result.cluster_data_hash_accepted == "hash_accepted"


class TestFromAnsible:
    def test_from_ansible_registration(self) -> None:
        data = dict(
            company_name="bla",
            contact="doubleBLA",
            email="TripleBLA",
            phone="QuadrupleBLA",
        )
        result = Registration.from_ansible(ansible_data=data)
        assert isinstance(result, Registration) is True
        assert result.company_name == data["company_name"]
        assert result.contact == data["contact"]
        assert result.email == data["email"]
        assert result.phone == data["phone"]


class TestFromHypercore:
    def test_create_from_hypercore_registration(self) -> None:
        data = dict(
            uuid="id",
            companyName="name",
            contact="contact",
            email="email",
            phone="phone",
            clusterID="id",
            clusterData="data",
            clusterDataHash="hash",
            clusterDataHashAccepted="hash_accepted",
        )
        result = Registration.from_hypercore(hypercore_data=data)
        assert isinstance(result, Registration) is True
        assert result.uuid == "id"
        assert result.company_name == "name"
        assert result.contact == "contact"
        assert result.email == "email"
        assert result.phone == "phone"
        assert result.cluster_id == "id"
        assert result.cluster_data == "data"
        assert result.cluster_data_hash == "hash"
        assert result.cluster_data_hash_accepted == "hash_accepted"


class TestToAnsible:
    def test_data_to_ansible_registration(self) -> None:
        registration_obj = Registration(
            company_name="bla",
            contact="doubleBLA",
            email="tripleBLA",
            phone="quadrupleBLA",
        )
        result = registration_obj.to_ansible()
        assert isinstance(result, dict)
        assert result == dict(
            company_name="bla",
            contact="doubleBLA",
            email="tripleBLA",
            phone="quadrupleBLA",
        )


class TestToHypercore:
    def test_to_hypercore_registration(self) -> None:
        registration_obj = Registration(
            company_name="bla",
            contact="doubleBLA",
            email="tripleBLA",
            phone="quadrupleBLA",
        )
        result = registration_obj.to_hypercore()
        assert isinstance(result, dict)
        assert result == dict(
            companyName="bla",
            contact="doubleBLA",
            email="tripleBLA",
            phone="quadrupleBLA",
        )


class TestSendRequest:
    def test_send_create_request_registration(self, rest_client) -> None:
        rest_client.create_record.return_value = {}
        registration_obj = Registration(
            company_name="bla",
            contact="doubleBLA",
            email="tripleBLA",
            phone="quadrupleBLA",
        )
        result = registration_obj.send_create_request(rest_client)
        assert isinstance(result, dict)
        assert result == dict()

    def test_send_update_request_registration(self, rest_client) -> None:
        rest_client.update_record.return_value = {}
        registration_obj = Registration(
            company_name="bla",
            contact="doubleBLA",
            email="tripleBLA",
            phone="quadrupleBLA",
        )
        result = registration_obj.send_update_request(rest_client)
        assert isinstance(result, dict)
        assert result == dict()

    def test_send_delete_request_registration(self, rest_client) -> None:
        rest_client.delete_record.return_value = {}
        registration_obj = Registration(
            company_name="bla",
            contact="doubleBLA",
            email="tripleBLA",
            phone="quadrupleBLA",
        )
        result = registration_obj.send_delete_request(rest_client)
        assert isinstance(result, dict)
        assert result == dict()
