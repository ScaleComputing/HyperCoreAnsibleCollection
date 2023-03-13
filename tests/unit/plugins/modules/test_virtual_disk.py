from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import virtual_disk
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


# Test main() module function.
class TestMain:
    @pytest.mark.parametrize(
        # test_parameters_virtual_disk
        # test_run_virtual_disk
        # Test different inputs for file and file_location. 
        ("file_name_test", "file_location_test", "state_test", "expected_result"),
        [
            # Present
            ("","","presen",(False, {'msg': 'value of state must be one of: present, absent, got: presen'})),
            ("","","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar","c:/location/foobar","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.vhd","c:/location/foobar.txt","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.txt","c:/location/foobar.txt","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.vmdk","c:/location/foobar.vmdk","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.img","c:/location/foobar.img","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.vhdx","c:/location/foobar.vhdx","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.vhd","c:/location/foobar.vhd","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.qcow2","c:/location/foobar.qcow2","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.qcow2",None,"present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            (None,"c:/location/foobar.qcow2","present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            (None, None ,"present", (True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            # Absent
            ("","","absen",(False, {'msg': 'value of state must be one of: present, absent, got: absen'})),
            ("","","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar","c:/location/foobar","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.vhd","c:/location/foobar.txt","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.txt","c:/location/foobar.txt","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.vmdk","c:/location/foobar.vmdk","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.img","c:/location/foobar.img","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.vhdx","c:/location/foobar.vhdx","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.vhd","c:/location/foobar.vhd","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.qcow2","c:/location/foobar.qcow2","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("foobar.qcow2",None,"absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            (None,"c:/location/foobar.qcow2","absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            (None, None ,"absent", (True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
        ],
    )
    def test_parameters_virtual_disk(self, run_main, mocker, file_location_test, file_name_test, state_test, expected_result) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            file_name=file_location_test,
            file_location=file_name_test,
            state=state_test,
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.hypercore_version.HyperCoreVersion.check_version"
        ).return_value = None
        success, results = run_main(virtual_disk, params)
        assert success == expected_result[0]
        assert results == expected_result[1]


# Test run() module function.
class TestRun:
    @pytest.mark.parametrize(
        # test_run_virtual_disk
        # Test run with differrent states and with existing or non-existing virtual disk.
        ("virtual_disk_dict", "state_test", "expected_result"),
        [
            # Present
                # Disk exists on cluster
            (dict(name="foobar.qcow2", uuid="123", blockSize="1000", capacityBytes="1000000", replicationFactor="2"), "present",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
                # Disk not exist on cluster
            (dict(), "present",(True, dict(changed=True, record=dict(), diff=dict(before=dict(), after=dict())))),
            # Absent
                 # Disk exists on cluster
            (dict(name="foobar.qcow2", uuid="123", blockSize="1000", capacityBytes="1000000", replicationFactor="2"), "absent",(True, dict(changed=True, record=dict(), diff=dict(before=dict(), after=dict())))),
                # Disk Not exist on cluster
            (dict(), "absent",(True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
        ],
    )
    def test_run_virtual_disk(self, create_module, rest_client, mocker, virtual_disk_dict, state_test, expected_result) -> None:
        module = create_module(
            params = dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                file_name="foobar.qcow2",
                file_location="c:/somewhere/foobar.qcow2",
                state=state_test,
            )
        )
        # Does virtual_disk exist on cluster or not.
        if virtual_disk_dict:
            virtual_disk_obj = VirtualDisk.from_hypercore(virtual_disk_dict)
        else:
            virtual_disk_obj = None
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.virtual_disk.VirtualDisk.get_by_name"
        ).return_value = virtual_disk_obj

        # Mock ensure_present or ensure_absent return value.
        mocker.patch(
            f"ansible_collections.scale_computing.hypercore.plugins.modules.virtual_disk.ensure_{state_test}"
        ).return_value = expected_result

        results = virtual_disk.run(module, rest_client)
        assert isinstance(results, tuple)
        assert results == expected_result


# Test ensure_present() module function.
class TestEnsurePresent:
    @pytest.mark.parametrize(
        # test_ensure_present_virtual_disk
        # Test different possible combinations with ensure_present.
        ("virtual_disk_dict", "updated_virtual_disk_dict", "disk_file_info", "expected_result", "expected_exception"),
        [
            # Disk exists on cluster
            (dict(name="foobar.qcow2", uuid="123", blockSize="1000", capacityBytes="1000000", replicationFactor="2"), dict(), dict(file_content="", file_size=""), (False, None, dict(before=None, after=None)), False),
            (dict(name="this.qcow2", uuid="123456", blockSize="1024", capacityBytes="1999999", replicationFactor="1"), dict(), dict(file_content="", file_size=""), (False, None, dict(before=None, after=None)), False),
            # Disk not exist on cluster
            (dict(), dict(name="foobar.qcow2", uuid="123", blockSize="1000", capacityBytes="1000000", replicationFactor="2"), dict(file_content=bytes(123), file_size=1024), (True, dict(name="foobar.qcow2", uuid="123", block_size="1000", size="1000000", replication_factor="2"), dict(before=None, after=dict(name="foobar.qcow2", uuid="123", block_size="1000", size="1000000", replication_factor="2"))), False),
            (dict(), dict(name="notfoobar.vhd", uuid="123456", blockSize="1024", capacityBytes="199999", replicationFactor="1"), dict(file_content=bytes(545647), file_size=10240), (True, dict(name="notfoobar.vhd", uuid="123456", block_size="1024", size="199999", replication_factor="1"), dict(before=None, after=dict(name="notfoobar.vhd", uuid="123456", block_size="1024", size="199999", replication_factor="1"))), False),
                # Disk file Exception
            (dict(), dict(name="foobar.qcow2", uuid="123", blockSize="1000", capacityBytes="1000000", replicationFactor="2"), dict(), (True, dict(name="foobar.qcow2", uuid="123", block_size="1000", size="1000000", replication_factor="2"), dict(before=None, after=dict(name="foobar.qcow2", uuid="123", block_size="1000", size="1000000", replication_factor="2"))), True),
            (dict(), dict(name="foobar.qcow2", uuid="123", blockSize="1000", capacityBytes="1000000", replicationFactor="2"), dict(file_content=bytes(123)), (True, dict(name="foobar.qcow2", uuid="123", block_size="1000", size="1000000", replication_factor="2"), dict(before=None, after=dict(name="foobar.qcow2", uuid="123", block_size="1000", size="1000000", replication_factor="2"))), True),
            (dict(), dict(name="foobar.qcow2", uuid="123", blockSize="1000", capacityBytes="1000000", replicationFactor="2"), dict(file_size=1024), (True, dict(name="foobar.qcow2", uuid="123", block_size="1000", size="1000000", replication_factor="2"), dict(before=None, after=dict(name="foobar.qcow2", uuid="123", block_size="1000", size="1000000", replication_factor="2"))), True),
        ],
    )
    def test_ensure_present_virtual_disk(self, create_module, rest_client, mocker, virtual_disk_dict, updated_virtual_disk_dict, disk_file_info, expected_result, expected_exception):
        module = create_module(
            params = dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                file_name="foobar.qcow2",
                file_location="c:/somewhere/foobar.qcow2",
                state="present",
            )
        )
        # Does virtual_disk exist on cluster or not.
        virtual_disk_obj = None
        if virtual_disk_dict:
            virtual_disk_obj = VirtualDisk.from_hypercore(virtual_disk_dict)
        else:
            # Mock read_disk_file(); returns a tuple() with file content and file size.
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.modules.virtual_disk.read_disk_file"
            ).return_value = (disk_file_info.get("file_content"), disk_file_info.get("file_size"))

        # Mock send_upload_request(); returns empty task tag.
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.virtual_disk.VirtualDisk.send_upload_request"
        ).return_value = dict(createdUUID="", taskTag="")

        # Mock wait_task_and_get_updated(); Performs wait_task and returns updated virtual disk.
        updated_virtual_disk = None
        if updated_virtual_disk_dict:
            updated_virtual_disk = VirtualDisk.from_hypercore(updated_virtual_disk_dict).to_ansible()
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.virtual_disk.wait_task_and_get_updated"
        ).return_value = updated_virtual_disk

        if expected_exception:
            with pytest.raises(ScaleComputingError, match=f"Invalid content or size for file: {module.params['file_name']}"):
                virtual_disk.ensure_present(module, rest_client, virtual_disk_obj)
        else:
            result = virtual_disk.ensure_present(module, rest_client, virtual_disk_obj)
            print(result, expected_result)
            assert isinstance(result, tuple)
            assert result == expected_result
