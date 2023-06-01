.. _scale_computing.hypercore.deprecation:

*****************
Deprecation Notes
*****************

Deprecation notes will list deprecated features in different HyperCore Collection releases
and guide users through migration.

Release 1.0.0
=============

Initial release, no deprecated features.

Release 1.1.0
=============

No deprecated features.

Release 1.2.0
=============

Module `scale_computing.hypercore.iso <../collections/scale_computing/hypercore/iso_module.html>`_
return value ``results`` is deprecated.
A new return value ``record`` is added as replacement.
The old ``results`` return value will remain available until release 3.0.0.

Only playbooks that store output from ``scale_computing.hypercore.iso``
module using ``register:`` keyword are affected.

Added deprecation note for modules
`scale_computing.hypercore.vm <../collections/scale_computing/hypercore/vm_module.html>`_ and
`scale_computing.hypercore.snapshot_schedule <../collections/scale_computing/hypercore/snapshot_schedule_module.html>`_.

Examples to help with transition to release 1.2.0
-------------------------------------------------

For ``scale_computing.hypercore.iso`` module:

.. code-block:: yaml

    # Store iso module output
    - name: Upload ISO {{ iso_filename }} to HyperCore
      scale_computing.hypercore.iso:
        name: "{{ iso_filename }}"
        source: /tmp/{{ iso_filename }}
        state: present
      register: uploaded_iso

    # Use iso module output, old syntax, valid until release < 3.0.0
    - name: Show upload result for ISO {{ iso_filename }} - deprecated syntax
      ansible.builtin.debug:
        msg: The uploaded_iso size={{ uploaded_iso.results.0.size }} - deprecated syntax

    # Use iso module output, new syntax, valid after release >= 1.2.0
    - name: Show upload result for ISO {{ iso_filename }}
      ansible.builtin.debug:
        msg: The uploaded_iso size={{ uploaded_iso.record.size }}

Release 1.3.0
=============

Role parameters were renamed to start with ``role_name_`` prefix.
For example, role `scale_computing.hypercore.version_update_single_node <../collections/scale_computing/hypercore/version_update_single_node_role.html>`_:

* ``scale_computing_hypercore_desired_version`` name was used before.
* ``version_update_single_node_desired_version`` name is used now.

Old names are still valid, but will be removed in future release 3.0.0.

Release 3.0.0 (not yet released)
================================

Module `scale_computing.hypercore.vm <../collections/scale_computing/hypercore/vm_module.html>`_
return value ``record`` content is changed from list with single item to a dict.

Module `scale_computing.hypercore.snapshot_schedule <../collections/scale_computing/hypercore/snapshot_schedule_module.html>`_
return value ``record`` content is changed from list with single item to a dict.

Only playbooks that store output from ``scale_computing.hypercore.vm``
(or ``scale_computing.hypercore.snapshot_schedule``) module using ``register:`` keyword are affected.

Examples to help with transition to release 3.0.0
-------------------------------------------------

For ``scale_computing.hypercore.vm`` module:

.. code-block:: yaml

    - name: Create VM {{ vm_name }}
      scale_computing.hypercore.vm:
        vm_name: "{{ vm_name }}"
        memory: "{{ '1 GB' | human_to_bytes }}"
        vcpu: 2
        disks:
          - type: virtio_disk
            disk_slot: 0
            size: "{{ '10 GB' | human_to_bytes }}"
        nics:
          - type: virtio
            vlan: 10
        state: present
        operating_system: os_other
      register: vm_result

    # Use vm module output, syntax valid until release < 3.0.0
    - name: Show VM {{ vm_name }} vCPU count - syntax valid until release < 3.0.0
      ansible.builtin.debug:
        msg: >-
          VM {{ vm_name }} has {{ vm_result.record.0.vcpu }} vCPUs -
          syntax valid until release < 3.0.0

    # Use vm module output, new syntax, valid after release >= 3.0.0
    - name: Show VM {{ vm_name }} vCPU count - syntax valid after release >= 3.0.0
      ansible.builtin.debug:
        msg: >-
          VM {{ vm_name }} has {{ vm_result.record.vcpu }} vCPUs -
          syntax valid after release >= 3.0.0

For ``scale_computing.hypercore.snapshot_schedule`` module:

.. code-block:: yaml

    - name: Setup snapshot schedule demo-snap-schedule
      scale_computing.hypercore.snapshot_schedule:
        name: demo-snap-schedule
        state: present
        recurrences:
          - name: weekly-tuesday
            frequency: "FREQ=WEEKLY;INTERVAL=1;BYDAY=TU"  # RFC-2445
            start: "2010-01-01 00:00:00"
            local_retention: "{{ 10 * 7*24*60*60 }}"  # 10 days, unit seconds
            remote_retention:  # optional, None or 0 means same as local_retention.
      register: demo_snapshot_schedule

    # Use snapshot_schedule module output, syntax valid until release < 3.0.0
    - name: Show snapshot schedule local retention - syntax valid until release < 3.0.0
      ansible.builtin.debug:
        msg: >-
          Snapshot schedule {{ demo_snapshot_schedule.record.0.name }} has local retention
          {{ demo_snapshot_schedule.record.0.recurrences.0.local_retention }} [sec] -
          syntax valid until release < 3.0.0

    # Use snapshot_schedule module output, new syntax, valid after release >= 3.0.0
    - name: Show snapshot schedule local retention - syntax valid after release >= 3.0.0
      ansible.builtin.debug:
        msg: >-
          Snapshot schedule {{ demo_snapshot_schedule.record.name }} has local retention
          {{ demo_snapshot_schedule.record.recurrences.0.local_retention }} [sec] -
          syntax valid after release >= 3.0.0
