# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from copy import deepcopy

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.virtual_disk import (
    VirtualDisk,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.errors import (
    ScaleComputingError,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestVirtualDisk:
    def setup_method(self):
        self.virtual_disk = VirtualDisk(
            name="vdisk-0",
            uuid="vdisk-uuid",
            block_size=1048576,
            size=104857600,
            replication_factor=2,
        )
        self.from_hypercore_dict = dict(
            blockSize=1048576,
            capacityBytes=104857600,
            name="vdisk-0",
            replicationFactor=2,
            totalAllocationBytes=10485760,
            uuid="vdisk-uuid",
        )
        # self.to_hypercore_dict = dict(
        #     name="vdisk-0",
        #     uuid="vdisk-uuid",
        #     block_size=1048576,
        #     size=104857600,
        #     replication_factor=2,
        # )
        self.to_ansible_dict = dict(
            name="vdisk-0",
            uuid="vdisk-uuid",
            block_size=1048576,
            size=104857600,
            replication_factor=2,
        )

    def test_virtual_disk_to_hypercore(self):
        with pytest.raises(NotImplementedError):
            self.virtual_disk.to_hypercore()

    def test_virtual_disk_from_hypercore_dict_not_empty(self):
        virtual_disk_from_hypercore = VirtualDisk.from_hypercore(
            self.from_hypercore_dict
        )
        assert self.virtual_disk == virtual_disk_from_hypercore

    # def test_virtual_disk_from_hypercore_dict_empty(self):
    #     assert VirtualDisk.from_hypercore({}) is None

    def test_virtual_disk_to_ansible(self):
        assert self.virtual_disk.to_ansible() == self.to_ansible_dict

    def test_virtual_disk_from_ansible(self):
        virtual_disk_from_ansible = VirtualDisk.from_ansible(self.from_hypercore_dict)
        assert "vdisk-0" == virtual_disk_from_ansible.name
        assert virtual_disk_from_ansible.uuid is None
        assert virtual_disk_from_ansible.block_size is None
        assert virtual_disk_from_ansible.size is None
        assert virtual_disk_from_ansible.replication_factor is None

    def test_get_state(self, rest_client):
        query = dict()
        rest_client.list_records.return_value = [self.from_hypercore_dict]

        result = VirtualDisk.get_state(rest_client, query)
        assert result == [
            {
                "name": "vdisk-0",
                "uuid": "vdisk-uuid",
                "block_size": 1048576,
                "size": 104857600,
                "replication_factor": 2,
            }
        ]

    def test_get_state_more_than_one_record(self, rest_client):
        expected_result = [
            {
                "name": "vdisk-0",
                "uuid": "vdisk-uuid",
                "block_size": 1048576,
                "size": 104857600,
                "replication_factor": 2,
            },
            {
                "name": "vdisk-1",
                "uuid": "vdisk-uuid-1",
                "block_size": 1048576,
                "size": 104857600,
                "replication_factor": 2,
            },
        ]
        hypercore_dict_0 = deepcopy(self.from_hypercore_dict)
        hypercore_dict_1 = deepcopy(self.from_hypercore_dict)
        hypercore_dict_1.update(
            {
                "name": "vdisk-1",
                "uuid": "vdisk-uuid-1",
            }
        )
        query = dict()
        rest_client.list_records.return_value = [
            hypercore_dict_0,
            hypercore_dict_1,
        ]
        result = VirtualDisk.get_state(rest_client, query)
        assert expected_result == result

    def test_get_state_no_record(self, rest_client):
        query = dict()
        rest_client.list_records.return_value = []

        result = VirtualDisk.get_state(rest_client, query)
        assert result == []


class TestGetByName:
    @pytest.mark.parametrize(
        # must_exist                        ... virtual disk info must exist on API.
        # virtual_disk_dict_from_api        ... virtual disk info from API
        # expected_missing_exception        ... virtual disk not exist exception
        # expected_unique_exception         ... virtual disk not unique exception
        # expected_result                   ... expected read_disk_file() return (file content and size)
        (
            "must_exist",
            "virtual_disk_dict_from_api",
            "expected_missing_exception",
            "expected_unique_exception",
            "expected_result",
        ),
        [
            # must_exist=True, does exist
            (
                True,
                dict(
                    name="foobar.qcow2",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.qcow2",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                True,
                dict(
                    name="foobar.vhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.vhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                True,
                dict(
                    name="foobar.xvhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.xvhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                True,
                dict(
                    name="foobar.img",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.img",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                True,
                dict(
                    name="foobar.vmdk",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.vmdk",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            # must_exist=True, does exist, not unique (exception)
            (
                True,
                dict(
                    name="foobar.qcow2",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.qcow2",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                True,
                dict(
                    name="foobar.vhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.vhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                True,
                dict(
                    name="foobar.xvhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.xvhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                True,
                dict(
                    name="foobar.img",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.img",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                True,
                dict(
                    name="foobar.vmdk",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.vmdk",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            # must_exist=True, does not exist (exception)
            (True, dict(), True, False, None),
            # must_exist=False, does exist
            (
                False,
                dict(
                    name="foobar.qcow2",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.qcow2",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                False,
                dict(
                    name="foobar.vhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.vhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                False,
                dict(
                    name="foobar.xvhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.xvhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                False,
                dict(
                    name="foobar.img",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.img",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                False,
                dict(
                    name="foobar.vmdk",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                False,
                dict(
                    name="foobar.vmdk",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            # must_exist=False, does not exist
            (False, dict(), False, False, None),
            # must_exist=False, does exist, not unique (exception)
            (
                False,
                dict(
                    name="foobar.qcow2",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.qcow2",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                False,
                dict(
                    name="foobar.vhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.vhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                False,
                dict(
                    name="foobar.xvhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.xvhd",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                False,
                dict(
                    name="foobar.img",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.img",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
            (
                False,
                dict(
                    name="foobar.vmdk",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
                False,
                True,
                dict(
                    name="foobar.vmdk",
                    uuid="1234-asd",
                    blockSize=10000,
                    capacityBytes=10000000,
                    replicationFactor=2,
                ),
            ),
        ],
    )
    def test_get_by_name_virtual_disk(
        self,
        rest_client,
        must_exist,
        virtual_disk_dict_from_api,
        expected_missing_exception,
        expected_unique_exception,
        expected_result,
    ):
        if expected_missing_exception:
            # Mock rest_client
            rest_client.list_records.return_value = [virtual_disk_dict_from_api]
            with pytest.raises(
                ScaleComputingError,
                match=f"Virtual disk with name {virtual_disk_dict_from_api.get('name', 'test_name.qcow2')} does not exist.",
            ):
                VirtualDisk.get_by_name(
                    rest_client,
                    virtual_disk_dict_from_api.get("name", "test_name.qcow2"),
                    must_exist,
                )
        elif expected_unique_exception:
            # Mock rest_client
            rest_client.list_records.return_value = [
                virtual_disk_dict_from_api,
                virtual_disk_dict_from_api,
            ]
            with pytest.raises(
                ScaleComputingError,
                match=f"Virtual disk {virtual_disk_dict_from_api['name']} has multiple instances and is not unique.",
            ):
                VirtualDisk.get_by_name(
                    rest_client, virtual_disk_dict_from_api["name"], must_exist
                )
        else:
            # Mock rest_client
            rest_client.list_records.return_value = [virtual_disk_dict_from_api]
            result = VirtualDisk.get_by_name(
                rest_client,
                virtual_disk_dict_from_api.get("name", "test_name.qcow2"),
                must_exist,
            )
            if virtual_disk_dict_from_api:
                expected_result = VirtualDisk.from_hypercore(expected_result)
            assert isinstance(result, VirtualDisk) or result is None
            assert result == expected_result


class TestSendUploadRequest:
    @pytest.mark.parametrize(
        # file_content                      ... virtual disk file content
        # file_size                         ... virtual disk file size
        # file_name                         ... virtual disk file name
        # expected_exception                ... expected missing values exception
        # expected_result                   ... expected send_upload_request() return (empty task tag)
        (
            "file_content",
            "file_size",
            "file_name",
            "expected_exception",
            "expected_result",
        ),
        [
            (bytes(123), 1024, "foobar.qcow2", False, dict(createdUUID="", taskTag="")),
            (
                bytes(456),
                3 * 1024,
                "foobar.vhd",
                False,
                dict(createdUUID="", taskTag=""),
            ),
            (
                bytes(123),
                999999,
                "foobar.xvhd",
                False,
                dict(createdUUID="", taskTag=""),
            ),
            (
                bytes(123),
                10111124,
                "foobar.img",
                False,
                dict(createdUUID="", taskTag=""),
            ),
            (
                bytes(123),
                10222224,
                "foobar.vmdk",
                False,
                dict(createdUUID="", taskTag=""),
            ),
            # Missing values exception
            (None, 1024, "foobar.qcow2", True, dict(createdUUID="", taskTag="")),
            (bytes(456), None, "foobar.vhd", True, dict(createdUUID="", taskTag="")),
            (bytes(123), 999999, None, True, dict(createdUUID="", taskTag="")),
            (None, None, None, True, dict(createdUUID="", taskTag="")),
        ],
    )
    def test_send_upload_request_virtual_disk(
        self,
        rest_client,
        file_content,
        file_size,
        file_name,
        expected_exception,
        expected_result,
    ):
        if expected_exception:
            with pytest.raises(
                ScaleComputingError,
                match="Missing some virtual disk file values inside upload request.",
            ):
                VirtualDisk.send_upload_request(
                    rest_client, file_content, file_size, file_name
                )
        else:
            # Mock rest_client.put_record()
            rest_client.put_record.return_value = dict(createdUUID="", taskTag="")
            result = VirtualDisk.send_upload_request(
                rest_client, file_content, file_size, file_name
            )
            assert isinstance(result, dict)
            assert result == expected_result


class TestSendDeleteRequest:
    @pytest.mark.parametrize(
        # virtual_disk                     ... virtual disk object
        # expected_result                  ... expected result (empty task)
        (
            "virtual_disk",
            "expected_exception",
            "expected_result",
        ),
        [
            (
                VirtualDisk(
                    uuid="asd-123123",
                    name="",
                    block_size="",
                    size="",
                    replication_factor="",
                ),
                False,
                dict(createdUUID="", taskTag=""),
            ),
            (
                VirtualDisk(
                    uuid="asd-123123",
                    name="",
                    block_size="",
                    size="",
                    replication_factor="",
                ),
                False,
                dict(createdUUID="", taskTag=""),
            ),
            (
                VirtualDisk(
                    uuid="asd-123123",
                    name="",
                    block_size="",
                    size="",
                    replication_factor="",
                ),
                False,
                dict(createdUUID="", taskTag=""),
            ),
            (
                VirtualDisk(
                    uuid="asd-123123",
                    name="",
                    block_size="",
                    size="",
                    replication_factor="",
                ),
                False,
                dict(createdUUID="", taskTag=""),
            ),
            (
                VirtualDisk(
                    uuid="ASD-67576657567-dsfsf-0EF",
                    name="",
                    block_size="",
                    size="",
                    replication_factor="",
                ),
                False,
                dict(createdUUID="", taskTag=""),
            ),
            # Missing UUID exception
            (
                VirtualDisk(
                    uuid="", name="", block_size="", size="", replication_factor=""
                ),
                True,
                None,
            ),
            (
                VirtualDisk(
                    uuid=None, name="", block_size="", size="", replication_factor=""
                ),
                True,
                None,
            ),
        ],
    )
    def test_send_delete_request_virtual_disk(
        self, rest_client, virtual_disk, expected_exception, expected_result
    ):
        if expected_exception:
            with pytest.raises(
                ScaleComputingError,
                match="Missing virtual disk UUID inside delete request.",
            ):
                virtual_disk.send_delete_request(rest_client)
        else:
            # Mock delete request
            rest_client.delete_record.return_value = dict(createdUUID="", taskTag="")
            result = virtual_disk.send_delete_request(rest_client)
            print(result)
            assert isinstance(result, dict)
            assert result == expected_result
