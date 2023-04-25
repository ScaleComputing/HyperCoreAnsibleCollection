from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_snapshot
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot import (
    VMSnapshot,
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
        # vm_name                           ... Virtual machine name
        # label                             ... Snapshot label
        # retain_for                        ... Retain length (in days)
        # replication                       ... Replication(True/False)
        # state                             ... state in module params
        # expected_result                   ... expected main() return
        ("vm_name", "label", "retain_for", "replication", "state", "expected_result"),
        [
            # Present
            ("test-vm", "this-label", 10, True, "present", (True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("test-vm", "this-label", 0, False, "present", (True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            # Absent
            ("test-vm", "this-label", 10, True, "absent", (True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
            ("test-vm", "this-label", 15, False, "absent", (True, dict(changed=False, record=dict(), diff=dict(before=dict(), after=dict())))),
        ],
    )
    def test_parameters_snapshot(
        self,
        run_main,
        vm_name,
        label,
        retain_for,
        replication,
        state,
        expected_result,
    ) -> None:
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name", username="user", password="pass"
            ),
            vm_name=vm_name,
            label=label,
            retain_for=retain_for,
            replication=replication,
            state=state,
        )
        success, results = run_main(vm_snapshot, params)
        print(success, results, expected_result)
        assert success == expected_result[0]
        assert results == expected_result[1]


# Test run() module function.
class TestRun:
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

        results = vm_snapshot.run(module, rest_client)
        assert isinstance(results, tuple)
        assert results == expected_result
