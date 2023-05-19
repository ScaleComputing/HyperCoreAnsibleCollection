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
        # file_name_test                    ... VDs file name in module params
        # file_location_test                ... VDs file location in module params
        # state_test                        ... state in module params
        # expected_result                   ... expected main() return
        ("file_name_test", "file_location_test", "state_test", "expected_result"),
        [
            # Present
            (
                "",
                "",
                "presen",
                (
                    False,
                    {
                        "msg": "value of state must be one of: present, absent, got: presen"
                    },
                ),
            ),
            (
                "",
                "",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar",
                "c:/location/foobar",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.vhd",
                "c:/location/foobar.txt",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.txt",
                "c:/location/foobar.txt",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.vmdk",
                "c:/location/foobar.vmdk",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.img",
                "c:/location/foobar.img",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.vhdx",
                "c:/location/foobar.vhdx",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.vhd",
                "c:/location/foobar.vhd",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.qcow2",
                "c:/location/foobar.qcow2",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.qcow2",
                None,
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "",
                "c:/location/foobar.qcow2",
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "",
                None,
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            # Absent
            (
                "",
                "",
                "absen",
                (
                    False,
                    {
                        "msg": "value of state must be one of: present, absent, got: absen"
                    },
                ),
            ),
            (
                "",
                "",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar",
                "c:/location/foobar",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.vhd",
                "c:/location/foobar.txt",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.txt",
                "c:/location/foobar.txt",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.vmdk",
                "c:/location/foobar.vmdk",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.img",
                "c:/location/foobar.img",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.vhdx",
                "c:/location/foobar.vhdx",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.vhd",
                "c:/location/foobar.vhd",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.qcow2",
                "c:/location/foobar.qcow2",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "foobar.qcow2",
                None,
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "",
                "c:/location/foobar.qcow2",
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            (
                "",
                None,
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
        ],
    )
    def test_parameters_virtual_disk(
        self,
        run_main,
        mocker,
        file_name_test,
        file_location_test,
        state_test,
        expected_result,
    ) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            name=file_name_test,
            source=file_location_test,
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
        # Test run with differrent states and with existing or non-existing virtual disk.
        # virtual_disk_dict                 ... virtual disk on cluster (empty dict = not exist)
        # state_test                        ... which state is sent to run()
        # expected_result                   ... expected run() return
        ("virtual_disk_dict", "state_test", "expected_result"),
        [
            # Present
            # Disk exists on cluster
            (
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                "present",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            # Disk not exist on cluster
            (
                dict(),
                "present",
                (
                    True,
                    dict(
                        changed=True,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            # Absent
            # Disk exists on cluster
            (
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                "absent",
                (
                    True,
                    dict(
                        changed=True,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
            # Disk Not exist on cluster
            (
                dict(),
                "absent",
                (
                    True,
                    dict(
                        changed=False,
                        record=dict(),
                        diff=dict(before=dict(), after=dict()),
                    ),
                ),
            ),
        ],
    )
    def test_run_virtual_disk(
        self,
        create_module,
        rest_client,
        mocker,
        virtual_disk_dict,
        state_test,
        expected_result,
    ) -> None:
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                name="foobar.qcow2",
                source="c:/somewhere/foobar.qcow2",
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
        # cluster_before_virtual_disk_dict  ... virtual disk on cluster before ensure_present()
        # cluster_after_virtual_disk_dict   ... virtual disk on cluster after ensure_present()
        # disk_file_info                    ... virtual disk file information (content and size)
        # expected_result                   ... expected ensure_present() return
        # expected_exception                ... expected exception within ensure_present()
        (
            "cluster_before_virtual_disk_dict",
            "cluster_after_virtual_disk_dict",
            "disk_file_info",
            "expected_result",
            "expected_exception",
        ),
        [
            # Disk exists on cluster
            (
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(file_size=""),
                (
                    False,
                    dict(
                        name="foobar.qcow2",
                        uuid="123",
                        block_size="1000",
                        size="1000000",
                        replication_factor="2",
                    ),
                    dict(
                        before=dict(
                            name="foobar.qcow2",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                        after=dict(
                            name="foobar.qcow2",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(
                    name="this.qcow2",
                    uuid="123456",
                    blockSize="1024",
                    capacityBytes="1999999",
                    replicationFactor="1",
                ),
                dict(
                    name="this.qcow2",
                    uuid="123456",
                    blockSize="1024",
                    capacityBytes="1999999",
                    replicationFactor="1",
                ),
                dict(file_size=""),
                (
                    False,
                    dict(
                        name="this.qcow2",
                        uuid="123456",
                        block_size="1024",
                        size="1999999",
                        replication_factor="1",
                    ),
                    dict(
                        before=dict(
                            name="this.qcow2",
                            uuid="123456",
                            block_size="1024",
                            size="1999999",
                            replication_factor="1",
                        ),
                        after=dict(
                            name="this.qcow2",
                            uuid="123456",
                            block_size="1024",
                            size="1999999",
                            replication_factor="1",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(
                    name="this.vhd",
                    uuid="asdf-1245",
                    blockSize="10240",
                    capacityBytes="1999999",
                    replicationFactor="3",
                ),
                dict(
                    name="this.vhd",
                    uuid="asdf-1245",
                    blockSize="10240",
                    capacityBytes="1999999",
                    replicationFactor="3",
                ),
                dict(file_size=""),
                (
                    False,
                    dict(
                        name="this.vhd",
                        uuid="asdf-1245",
                        block_size="10240",
                        size="1999999",
                        replication_factor="3",
                    ),
                    dict(
                        before=dict(
                            name="this.vhd",
                            uuid="asdf-1245",
                            block_size="10240",
                            size="1999999",
                            replication_factor="3",
                        ),
                        after=dict(
                            name="this.vhd",
                            uuid="asdf-1245",
                            block_size="10240",
                            size="1999999",
                            replication_factor="3",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(
                    name="this.xvhd",
                    uuid="asdf-1245",
                    blockSize="10240",
                    capacityBytes="1999999",
                    replicationFactor="3",
                ),
                dict(
                    name="this.xvhd",
                    uuid="asdf-1245",
                    blockSize="10240",
                    capacityBytes="1999999",
                    replicationFactor="3",
                ),
                dict(file_size=""),
                (
                    False,
                    dict(
                        name="this.xvhd",
                        uuid="asdf-1245",
                        block_size="10240",
                        size="1999999",
                        replication_factor="3",
                    ),
                    dict(
                        before=dict(
                            name="this.xvhd",
                            uuid="asdf-1245",
                            block_size="10240",
                            size="1999999",
                            replication_factor="3",
                        ),
                        after=dict(
                            name="this.xvhd",
                            uuid="asdf-1245",
                            block_size="10240",
                            size="1999999",
                            replication_factor="3",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(
                    name="this.img",
                    uuid="asdf-1245",
                    blockSize="10240",
                    capacityBytes="1999999",
                    replicationFactor="3",
                ),
                dict(
                    name="this.img",
                    uuid="asdf-1245",
                    blockSize="10240",
                    capacityBytes="1999999",
                    replicationFactor="3",
                ),
                dict(file_size=""),
                (
                    False,
                    dict(
                        name="this.img",
                        uuid="asdf-1245",
                        block_size="10240",
                        size="1999999",
                        replication_factor="3",
                    ),
                    dict(
                        before=dict(
                            name="this.img",
                            uuid="asdf-1245",
                            block_size="10240",
                            size="1999999",
                            replication_factor="3",
                        ),
                        after=dict(
                            name="this.img",
                            uuid="asdf-1245",
                            block_size="10240",
                            size="1999999",
                            replication_factor="3",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(
                    name="this.vmdk",
                    uuid="asdf-1245",
                    blockSize="10240",
                    capacityBytes="1999999",
                    replicationFactor="3",
                ),
                dict(
                    name="this.vmdk",
                    uuid="asdf-1245",
                    blockSize="10240",
                    capacityBytes="1999999",
                    replicationFactor="3",
                ),
                dict(file_size=""),
                (
                    False,
                    dict(
                        name="this.vmdk",
                        uuid="asdf-1245",
                        block_size="10240",
                        size="1999999",
                        replication_factor="3",
                    ),
                    dict(
                        before=dict(
                            name="this.vmdk",
                            uuid="asdf-1245",
                            block_size="10240",
                            size="1999999",
                            replication_factor="3",
                        ),
                        after=dict(
                            name="this.vmdk",
                            uuid="asdf-1245",
                            block_size="10240",
                            size="1999999",
                            replication_factor="3",
                        ),
                    ),
                ),
                False,
            ),
            # Disk not exist on cluster
            (
                dict(),
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(file_size=1024),
                (
                    True,
                    dict(
                        name="foobar.qcow2",
                        uuid="123",
                        block_size="1000",
                        size="1000000",
                        replication_factor="2",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="foobar.qcow2",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(),
                dict(
                    name="notfoobar.vhd",
                    uuid="123456",
                    blockSize="1024",
                    capacityBytes="199999",
                    replicationFactor="1",
                ),
                dict(file_size=10240),
                (
                    True,
                    dict(
                        name="notfoobar.vhd",
                        uuid="123456",
                        block_size="1024",
                        size="199999",
                        replication_factor="1",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="notfoobar.vhd",
                            uuid="123456",
                            block_size="1024",
                            size="199999",
                            replication_factor="1",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(),
                dict(
                    name="notfoobar.xvhd",
                    uuid="123456",
                    blockSize="1024",
                    capacityBytes="199999",
                    replicationFactor="1",
                ),
                dict(file_size=10240),
                (
                    True,
                    dict(
                        name="notfoobar.xvhd",
                        uuid="123456",
                        block_size="1024",
                        size="199999",
                        replication_factor="1",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="notfoobar.xvhd",
                            uuid="123456",
                            block_size="1024",
                            size="199999",
                            replication_factor="1",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(),
                dict(
                    name="notfoobar.img",
                    uuid="123456",
                    blockSize="1024",
                    capacityBytes="199999",
                    replicationFactor="1",
                ),
                dict(file_size=10240),
                (
                    True,
                    dict(
                        name="notfoobar.img",
                        uuid="123456",
                        block_size="1024",
                        size="199999",
                        replication_factor="1",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="notfoobar.img",
                            uuid="123456",
                            block_size="1024",
                            size="199999",
                            replication_factor="1",
                        ),
                    ),
                ),
                False,
            ),
            (
                dict(),
                dict(
                    name="notfoobar.vmdk",
                    uuid="123456",
                    blockSize="1024",
                    capacityBytes="199999",
                    replicationFactor="1",
                ),
                dict(file_size=10240),
                (
                    True,
                    dict(
                        name="notfoobar.vmdk",
                        uuid="123456",
                        block_size="1024",
                        size="199999",
                        replication_factor="1",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="notfoobar.vmdk",
                            uuid="123456",
                            block_size="1024",
                            size="199999",
                            replication_factor="1",
                        ),
                    ),
                ),
                False,
            ),
            # Disk file Exception
            (
                dict(),
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(),
                (
                    True,
                    dict(
                        name="foobar.qcow2",
                        uuid="123",
                        block_size="1000",
                        size="1000000",
                        replication_factor="2",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="foobar.qcow2",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                    ),
                ),
                True,
            ),
            (
                dict(),
                dict(
                    name="foobar.vhd",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(),
                (
                    True,
                    dict(
                        name="foobar.vhd",
                        uuid="123",
                        block_size="1000",
                        size="1000000",
                        replication_factor="2",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="foobar.vhd",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                    ),
                ),
                True,
            ),
            (
                dict(),
                dict(
                    name="foobar.xvhd",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(),
                (
                    True,
                    dict(
                        name="foobar.xvhd",
                        uuid="123",
                        block_size="1000",
                        size="1000000",
                        replication_factor="2",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="foobar.xvhd",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                    ),
                ),
                True,
            ),
            (
                dict(),
                dict(
                    name="foobar.img",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(),
                (
                    True,
                    dict(
                        name="foobar.img",
                        uuid="123",
                        block_size="1000",
                        size="1000000",
                        replication_factor="2",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="foobar.img",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                    ),
                ),
                True,
            ),
            (
                dict(),
                dict(
                    name="foobar.vmdk",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(),
                (
                    True,
                    dict(
                        name="foobar.vmdk",
                        uuid="123",
                        block_size="1000",
                        size="1000000",
                        replication_factor="2",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="foobar.vmdk",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                    ),
                ),
                True,
            ),
            (
                dict(),
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(),
                (
                    True,
                    dict(
                        name="foobar.qcow2",
                        uuid="123",
                        block_size="1000",
                        size="1000000",
                        replication_factor="2",
                    ),
                    dict(
                        before=None,
                        after=dict(
                            name="foobar.qcow2",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                    ),
                ),
                True,
            ),
        ],
    )
    def test_ensure_present_virtual_disk(
        self,
        create_module,
        rest_client,
        mocker,
        cluster_before_virtual_disk_dict,
        cluster_after_virtual_disk_dict,
        disk_file_info,
        expected_result,
        expected_exception,
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                name="foobar.qcow2",
                source="c:/somewhere/foobar.qcow2",
                state="present",
            )
        )
        # Does virtual_disk exist on cluster or not.
        cluster_before_virtual_disk_obj = None
        if cluster_before_virtual_disk_dict:
            cluster_before_virtual_disk_obj = VirtualDisk.from_hypercore(
                cluster_before_virtual_disk_dict
            )
        else:
            # Mock read_disk_file(); returns a tuple() with file content and file size.
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.modules.virtual_disk.read_disk_file"
            ).return_value = disk_file_info.get("file_size")

        # Mock send_upload_request(); returns empty task tag.
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.virtual_disk.VirtualDisk.send_upload_request"
        ).return_value = dict(createdUUID="", taskTag="")

        # Mock wait_task_and_get_updated(); Performs wait_task and returns updated virtual disk.
        cluster_after_virtual_disk = None
        if cluster_after_virtual_disk_dict:
            cluster_after_virtual_disk = VirtualDisk.from_hypercore(
                cluster_after_virtual_disk_dict
            ).to_ansible()
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.virtual_disk.wait_task_and_get_updated"
        ).return_value = cluster_after_virtual_disk

        if expected_exception:
            with pytest.raises(
                ScaleComputingError,
                match=f"Invalid size for file: {module.params['source']}",
            ):
                virtual_disk.ensure_present(
                    module, rest_client, cluster_before_virtual_disk_obj
                )
        else:
            result = virtual_disk.ensure_present(
                module, rest_client, cluster_before_virtual_disk_obj
            )
            assert isinstance(result, tuple)
            assert result == expected_result


# Test ensure_absent() module function.
class TestEnsureAbsent:
    @pytest.mark.parametrize(
        # cluster_before_virtual_disk_dict  ... virtual disk on cluster before ensure_absent()
        # cluster_after_virtual_disk_dict   ... virtual disk on cluster after ensure_absent()
        # expected_result                   ... expected ensure_absent() return
        (
            "cluster_before_virtual_disk_dict",
            "cluster_after_virtual_disk_dict",
            "expected_result",
        ),
        [
            # VD already deleted / not exist
            (dict(), dict(), (False, None, dict(before=None, after=None))),
            # VD exists / needs to be deleted
            (
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                dict(),
                (
                    True,
                    None,
                    dict(
                        before=dict(
                            name="foobar.qcow2",
                            uuid="123",
                            block_size="1000",
                            size="1000000",
                            replication_factor="2",
                        ),
                        after=None,
                    ),
                ),
            ),
            (
                dict(
                    name="foobar.vhd",
                    uuid="asdf-123-qwe",
                    blockSize="1024",
                    capacityBytes="12222000000",
                    replicationFactor="5",
                ),
                dict(),
                (
                    True,
                    None,
                    dict(
                        before=dict(
                            name="foobar.vhd",
                            uuid="asdf-123-qwe",
                            block_size="1024",
                            size="12222000000",
                            replication_factor="5",
                        ),
                        after=None,
                    ),
                ),
            ),
            (
                dict(
                    name="foobar.xvhd",
                    uuid="fake-uuid-456",
                    blockSize="2056",
                    capacityBytes="1500000000",
                    replicationFactor="3",
                ),
                dict(),
                (
                    True,
                    None,
                    dict(
                        before=dict(
                            name="foobar.xvhd",
                            uuid="fake-uuid-456",
                            block_size="2056",
                            size="1500000000",
                            replication_factor="3",
                        ),
                        after=None,
                    ),
                ),
            ),
            (
                dict(
                    name="foobar.img",
                    uuid="3456456",
                    blockSize="200056",
                    capacityBytes="1123000000",
                    replicationFactor="1",
                ),
                dict(),
                (
                    True,
                    None,
                    dict(
                        before=dict(
                            name="foobar.img",
                            uuid="3456456",
                            block_size="200056",
                            size="1123000000",
                            replication_factor="1",
                        ),
                        after=None,
                    ),
                ),
            ),
            (
                dict(
                    name="foobar.vmdk",
                    uuid="1233343",
                    blockSize="399999",
                    capacityBytes="1455000000",
                    replicationFactor="0",
                ),
                dict(),
                (
                    True,
                    None,
                    dict(
                        before=dict(
                            name="foobar.vmdk",
                            uuid="1233343",
                            block_size="399999",
                            size="1455000000",
                            replication_factor="0",
                        ),
                        after=None,
                    ),
                ),
            ),
        ],
    )
    def test_ensure_absent_virtual_disk(
        self,
        create_module,
        rest_client,
        mocker,
        cluster_before_virtual_disk_dict,
        cluster_after_virtual_disk_dict,
        expected_result,
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                name="foobar.qcow2",
                source="c:/somewhere/foobar.qcow2",
                state="absent",
            )
        )
        # Does virtual_disk exist on cluster or not.
        cluster_before_virtual_disk_obj = None
        if cluster_before_virtual_disk_dict:
            cluster_before_virtual_disk_obj = VirtualDisk.from_hypercore(
                cluster_before_virtual_disk_dict
            )

        # Mock send_delete_request(); returns empty task tag.
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.virtual_disk.VirtualDisk.send_delete_request"
        ).return_value = dict(createdUUID="", taskTag="")

        # Mock wait_task_and_get_updated(); Performs wait_task and returns updated virtual disk.
        cluster_after_virtual_disk = None
        if cluster_after_virtual_disk_dict:
            cluster_after_virtual_disk = VirtualDisk.from_hypercore(
                cluster_after_virtual_disk_dict
            ).to_ansible()
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.modules.virtual_disk.wait_task_and_get_updated"
        ).return_value = cluster_after_virtual_disk

        result = virtual_disk.ensure_absent(
            module, rest_client, cluster_before_virtual_disk_obj
        )
        assert isinstance(result, tuple)
        assert result == expected_result


# Test wait_task_and_get_updated() module function.
class TestWaitTaskAndGetUpdated:
    @pytest.mark.parametrize(
        # updated_virtual_disk_dict         ... virtual disk after preset / absent action
        # must_exist                        ... virtual disk must exist on cluster (True/False)
        # expected_result                   ... expected wait_task_and_get_updated() return
        ("updated_virtual_disk_dict", "must_exist", "expected_result"),
        [
            # After preset action, Must exist=True
            (
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                True,
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            (
                dict(
                    name="foobar.vhd",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                True,
                dict(
                    name="foobar.vhd",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            (
                dict(
                    name="foobar.xvhd",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                True,
                dict(
                    name="foobar.xvhd",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            (
                dict(
                    name="foobar.img",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                True,
                dict(
                    name="foobar.img",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            (
                dict(
                    name="foobar.vmdk",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                True,
                dict(
                    name="foobar.vmdk",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            # After absent action, Must exist=False
            (
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                False,
                dict(
                    name="foobar.qcow2",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            (
                dict(
                    name="foobar.vhd",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                False,
                dict(
                    name="foobar.vhd",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            (
                dict(
                    name="foobar.xvhd",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                False,
                dict(
                    name="foobar.xvhd",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            (
                dict(
                    name="foobar.img",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                False,
                dict(
                    name="foobar.img",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            (
                dict(
                    name="foobar.vmdk",
                    uuid="123",
                    blockSize="1000",
                    capacityBytes="1000000",
                    replicationFactor="2",
                ),
                False,
                dict(
                    name="foobar.vmdk",
                    uuid="123",
                    block_size="1000",
                    size="1000000",
                    replication_factor="2",
                ),
            ),
            # Corner cases where VD exists after absent or not exist after present are handled within get_by_name().
            # And should be tested separately within that function.
        ],
    )
    def test_wait_task_and_get_updated_virtual_disk(
        self,
        create_module,
        rest_client,
        mocker,
        updated_virtual_disk_dict,
        must_exist,
        expected_result,
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                name="foobar.qcow2",
                source="c:/somewhere/foobar.qcow2",
                state="present",
            )
        )
        updated_virtual_disk_obj = VirtualDisk.from_hypercore(updated_virtual_disk_dict)

        # Empty task, virtual disk API endpoint always returns empty.
        task = dict(createdUUID="", taskTag="")

        # Mock wait_task()
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = dict(createdUUID="", taskTag="")

        # Mock virtual disk get_by_name()
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.virtual_disk.VirtualDisk.get_by_name"
        ).return_value = updated_virtual_disk_obj

        result = virtual_disk.wait_task_and_get_updated(
            rest_client, module, task, must_exist
        )
        assert result == expected_result


# Test read_disk_file() module function.
class TestReadDiskFile:
    @pytest.mark.parametrize(
        # file_location                     ... location of the virtual disk file.
        # file size                         ... size of disk file
        # file content                      ... disk file content
        # expected_exception                ... is file not found exception expected.
        # expected_result                   ... expected read_disk_file() return (file content and size)
        (
            "file_location",
            "file_size",
            "expected_exception",
            "expected_result",
        ),
        [
            # Disk file is found
            ("c:/here/foobar.qcow2", 1024, False, 1024),
            (
                "d:/somwhere/here/foobar.vhd",
                3 * 1024,
                False,
                3 * 1024,
            ),
            (
                "b:/over/here/foobar.xvhd",
                1020004,
                False,
                1020004,
            ),
            ("q:/maybe/here/foobar.img", 65999, False, 65999),
            ("c:/foobar.vmdk", 99999999, False, 99999999),
            # Disk file is not found
            ("c:/here/foobar.qcow2", 1024, True, None),
            ("d:/somwhere/here/foobar.vhd", 3 * 1024, True, None),
            ("b:/over/here/foobar.xvhd", 1020004, True, None),
            ("q:/maybe/here/foobar.img", 65999, True, None),
            ("c:/foobar.vmdk", 99999999, True, None),
        ],
    )
    def test_read_disk_file_virtual_disk(
        self,
        create_module,
        mocker,
        file_location,
        file_size,
        expected_exception,
        expected_result,
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                name="foobar.qcow2",
                source=file_location,
                state="present",
            )
        )
        if expected_exception:
            with pytest.raises(
                ScaleComputingError,
                match=f"Disk file {module.params['source']} not found.",
            ):
                virtual_disk.read_disk_file(module)
        else:
            # Mock getsize() and return mocked size
            mocker.patch("os.path.getsize", return_value=file_size)
            # Mock file open() and read data
            result = virtual_disk.read_disk_file(module)
            assert result == expected_result
