=======================================
Scale_Computing.Hypercore Release Notes
=======================================

.. contents:: Topics


v1.1.0
======

Release Summary
---------------

Feature release with minor changes and small bugfixes.

Minor Changes
-------------

- 'machine_type' option added to vm module.
- 'put' now implemented and added to 'action' option in api module.
- 'source' option added to api module.

Bugfixes
--------

- CD_ROM should be created without passing the size option to vm_disk module.
- Changing the 'tiering_priority' does not require machine restart and values are now mapped properly.
- Idempotence for module snapshot_schedule.
- Issues with 'cloud_init' option now fixed, created IDE_DISK is not overriden.
- Make sure enlarging the virtual disk does not require machine restart.
- Makes sure that vm_disk module reports changes when ISO is detached.
- Option 'attach_guest_tools' now works as intended with Windows systems.
- Timeout is now properly applied and overrides the default.

v1.0.0
======

Release Summary
---------------

Initial release

New Plugins
-----------

Inventory
~~~~~~~~~

- scale_computing.hypercore.hypercore - Inventory source for Scale Computing HyperCore.

New Modules
-----------

- scale_computing.hypercore.api - API interaction with Scale Computing HyperCore
- scale_computing.hypercore.iso - Manage ISO images on HyperCore API
- scale_computing.hypercore.iso_info - Retrieve ISO images
- scale_computing.hypercore.node_info - Returns information about the nodes in a cluster.
- scale_computing.hypercore.remote_cluster_info - Retrieve a list of remote clusters.
- scale_computing.hypercore.snapshot_schedule - Manage snap schedule to configure the desired schedule of snapshot creation.
- scale_computing.hypercore.snapshot_schedule_info - Retrieve information about an automated VM snapshot schedule.
- scale_computing.hypercore.task_wait - Wait for a HyperCore TaskTag to be finished.
- scale_computing.hypercore.vm - Create, update or delete a VM.
- scale_computing.hypercore.vm_boot_devices - Manage HyperCore VM's boot devices
- scale_computing.hypercore.vm_clone - Handles cloning of the VM
- scale_computing.hypercore.vm_disk - Manage VM's disks
- scale_computing.hypercore.vm_export - Handles export of the virtual machine
- scale_computing.hypercore.vm_import - Handles import of the virtual machine
- scale_computing.hypercore.vm_info - Retrieve information about the VMs.
- scale_computing.hypercore.vm_nic - Handles actions over network interfaces
- scale_computing.hypercore.vm_nic_info - Returns info about NIC
- scale_computing.hypercore.vm_node_affinity - Update virtual machine's node affinity
- scale_computing.hypercore.vm_params - Manage VM's parameters
- scale_computing.hypercore.vm_replication - Handles VM replications
- scale_computing.hypercore.vm_replication_info - Returns info about replication of a specific VM
