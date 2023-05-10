from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import vm_snapshot
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot import (
    VMSnapshot,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.vm import VM
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
            (
                "test-vm",
                "this-label",
                10,
                True,
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
                "test-vm",
                "this-label",
                0,
                False,
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
                "test-vm",
                "this-label",
                10,
                True,
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
                "test-vm",
                "this-label",
                15,
                False,
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
    @pytest.mark.parametrize(
        # state                             ... which state is sent to run()
        # snapshot_list                     ... get_snapshot query return
        # expected_exception                ... is get_snapshot exception expected
        # expected_result                   ... expected run() return
        ("state", "snapshot_list", "expected_exception", "expected_result"),
        [
            # Present; No exception.
            ("present", [], False, (True, dict(), dict())),
            ("present", [dict(label="this-label")], False, (False, dict(), dict())),
            # Present; with exception.
            (
                "present",
                [dict(label="this-label"), dict(label="this-label")],
                True,
                (False, dict(), dict()),
            ),
            # Absent; No exception.
            ("absent", [], False, (False, dict(), dict())),
            ("absent", [dict(label="this-label")], False, (True, dict(), dict())),
            # Absent; with exception.
            (
                "absent",
                [dict(label="this-label"), dict(label="this-label")],
                True,
                (False, dict(), dict()),
            ),
        ],
    )
    def test_run_virtual_disk(
        self,
        create_module,
        rest_client,
        mocker,
        state,
        snapshot_list,
        expected_exception,
        expected_result,
    ) -> None:
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                vm_name="this-VM",
                label="this-label",
                retain_for=30,
                replication=True,
                state=state,
            )
        )

        # Mock VM
        mock_VM = mocker.MagicMock(spec=VM)
        mock_VM.uuid = "123"
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm.VM.get_by_name"
        ).return_value = mock_VM

        # Mock get_snapshot
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.get_snapshots_by_query"
        ).return_value = snapshot_list

        # Check for snapshot exception.
        if expected_exception:
            with pytest.raises(
                ScaleComputingError,
                match=f"Virtual machine - {module.params['vm_name']} - has more than one snapshot with label - {module.params['label']}.",
            ):
                vm_snapshot.run(module, rest_client)
        else:
            # Mock ensure_present and ensure_absent
            mocker.patch(
                f"ansible_collections.scale_computing.hypercore.plugins.modules.vm_snapshot.ensure_{state}"
            ).return_value = expected_result

            results = vm_snapshot.run(module, rest_client)
            print(results, expected_result)
            assert isinstance(results, tuple)
            assert results == expected_result


# Test ensure_present() module function.
class TestEnsurePresent:
    @pytest.mark.parametrize(
        # label                             ... Snapsho label
        # snapshot_list                     ... get_snapshot query return
        # after                             ... after returned by API
        # expected_result                   ... expected resulted returned by function
        ("label", "snapshot_list", "after", "expected_result"),
        [
            # Create snapshot.
            (
                "this-label",
                [],
                [VMSnapshot(vm_name="this-vm", label="this-label")],
                (
                    True,
                    VMSnapshot(vm_name="this-vm", label="this-label"),
                    dict(
                        before=None,
                        after=VMSnapshot(vm_name="this-vm", label="this-label"),
                    ),
                ),
            ),
            # Snapshot already exists, do nothing.
            (
                "this-label",
                [VMSnapshot(vm_name="this-vm", label="this-label")],
                [VMSnapshot(vm_name="this-vm", label="this-label")],
                (
                    False,
                    VMSnapshot(vm_name="this-vm", label="this-label"),
                    dict(
                        before=VMSnapshot(vm_name="this-vm", label="this-label"),
                        after=VMSnapshot(vm_name="this-vm", label="this-label"),
                    ),
                ),
            ),
        ],
    )
    def test_ensure_present_vm_snapshot(
        self,
        create_module,
        rest_client,
        mocker,
        label,
        snapshot_list,
        after,
        expected_result,
    ):
        # Mock module
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                vm_name="this-VM",
                label=label,
                retain_for=None,
                replication=True,
                state="present",
            )
        )
        # Mock VM
        vm_object = mocker.MagicMock(spec=VM)
        vm_object.uuid = "123"

        # Mock send_create_request and task
        task = dict()
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.send_create_request"
        ).return_value = task
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = None

        # Mock after
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.get_snapshots_by_query"
        ).return_value = after

        result = vm_snapshot.ensure_present(
            module, rest_client, vm_object, snapshot_list
        )
        assert isinstance(result, tuple)
        assert result == expected_result


# Test ensure_absent() module function.
class TestEnsureAbsent:
    @pytest.mark.parametrize(
        # label                             ... Snapsho label
        # snapshot_list                     ... get_snapshot query return
        # after                             ... after returned by API
        # expected_result                   ... expected resulted returned by function
        ("label", "snapshot_list", "after", "expected_result"),
        [
            # Snapshot already absent, do nothing.
            ("this-label", [], [], (False, None, dict(before=None, after=None))),
            # Delete snapshot.
            (
                "this-label",
                [dict(vm_name="this-vm", label="this-label", snapshot_uuid="123")],
                [],
                (
                    True,
                    None,
                    dict(
                        before=dict(
                            vm_name="this-vm", label="this-label", snapshot_uuid="123"
                        ),
                        after=None,
                    ),
                ),
            ),
        ],
    )
    def test_ensure_absent_vm_snapshot(
        self,
        create_module,
        rest_client,
        mocker,
        label,
        snapshot_list,
        after,
        expected_result,
    ):
        # Mock module
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://my.host.name", username="user", password="pass"
                ),
                vm_name="this-VM",
                label=label,
                retain_for=None,
                replication=True,
                state="absent",
            )
        )
        # Mock VM
        vm_object = mocker.MagicMock(spec=VM)
        vm_object.uuid = "123"

        # Mock send_delete_request and task
        task = dict()
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.send_delete_request"
        ).return_value = task
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.task_tag.TaskTag.wait_task"
        ).return_value = None

        # Mock after
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.vm_snapshot.VMSnapshot.get_snapshots_by_query"
        ).return_value = after

        result = vm_snapshot.ensure_absent(
            module, rest_client, vm_object, snapshot_list
        )
        print(result, expected_result)
        assert isinstance(result, tuple)
        assert result == expected_result
