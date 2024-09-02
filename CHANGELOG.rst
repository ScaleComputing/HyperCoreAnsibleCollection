========================================
Scale\_Computing.Hypercore Release Notes
========================================

.. contents:: Topics

v1.6.0
======

Minor Changes
-------------

- Role `cluster_config` invokes multiple cluster configuration modules. If one module fails, the role now continues with other modules to apply as many configuration changes as possible. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/322)

v1.5.0
======

Major Changes
-------------

- Added roles url2template and template2vm. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/310)

v1.4.0
======

Major Changes
-------------

- Allow changing VM `machine_type` using vm and vm_param modules. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/287)

Minor Changes
-------------

- Added `vtpm` disk type to vm and vm_disks modules. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/286)
- Fix `vm_rebooted` output value. The meaning needs to be "was VM rebooted". Some modules were still returning "VM needs to be rebooted (if it is running) to apply (some) changes".
- vm_nic module fails with descriptive message (no crash) if VM is missing.

v1.3.0
======

Major Changes
-------------

- Added a role for checking if local time is within required time interval. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/167)
- Added a role for updating single-node systems. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/136)
- Added version_update, version_update_info and version_update_status_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/135)
- Added virtual_disk module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/153)
- Added virtual_disk_attach module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/212)
- Added vm_snapshot module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/217)
- Added vm_snapshot_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/166)

Minor Changes
-------------

- Added option select to version_update_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/189)
- Added preserve_mac_address option to vm_clone module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/187)
- Added snapshot cloning to vm_clone. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/219)
- Extend vm and vm_info modules output with replication_source_vm_uuid field. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/185)

Bugfixes
--------

- Convert SC_TIMEOUT environ variable to float, thus resolving inventory parse error when SC_TIMEOUT was defined. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/231)
- This fix now handles case if no update_status.json exists yet. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/174)

v1.2.0
======

Release Summary
---------------

Feature release with new modules and roles, minor changes and small bugfixes.

Major Changes
-------------

- Added a role for cluster configuration (registration data, DNS resolver, SMPT server, email alert recipients, etc).
- Added certificate module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/119)
- Added cluster_name and cluster_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/112)
- Added cluster_shutdown module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/117)
- Added dns_config and dns_config_info modules. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/73)
- Added email_alert and email_alert_info modules. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/99)
- Added oidc_config and oidc_config_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/106)
- Added registration and registration_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/98)
- Added smtp and smtp_info modules. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/93)
- Added support_tunnel module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/92)
- Added support_tunnel_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/92)
- Added syslog_server and syslog_server_info modules. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/120)
- Added time_server and time_server_info modules. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/82)
- Added time_zone and time_zone_info modules. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/82)
- Added user module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/79)
- Added user_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/74)
- Added virtual_disk_info module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/84)
- Deprecate results value and add record value in iso module return values. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/183)

Minor Changes
-------------

- Fixed timeout error in cluster_shutdown module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/127)
- Updated version check in cluster_name module. (https://github.com/ScaleComputing/HyperCoreAnsibleCollection/pull/123)

Deprecated Features
-------------------

- Added deprecation note for return value, for modules `scale_computing.hypercore.vm <../collections/scale_computing/hypercore/vm_module.html>`_ and `scale_computing.hypercore.snapshot_schedule <../collections/scale_computing/hypercore/snapshot_schedule_module.html>`_.
- Module `scale_computing.hypercore.iso <../collections/scale_computing/hypercore/iso_module.html>`_ return value ``results`` is deprecated. A new return value ``record`` is added as replacement.

New Modules
-----------

- scale_computing.hypercore.cluster_info - Retrieve cluster info.
- scale_computing.hypercore.cluster_name - Update cluster name.
- scale_computing.hypercore.cluster_shutdown - Shutdown the cluster.
- scale_computing.hypercore.dns_config - Modify DNS configuration on HyperCore API
- scale_computing.hypercore.dns_config_info - List DNS configuration on HyperCore API
- scale_computing.hypercore.email_alert - Create, update, delete or send test emails to Email Alert Recipients on HyperCore API.
- scale_computing.hypercore.email_alert_info - List Email Alert Recipients on HyperCore API
- scale_computing.hypercore.smtp - Modify SMTP configuration on HyperCore API.
- scale_computing.hypercore.smtp_info - List SMTP configuration on HyperCore API.
- scale_computing.hypercore.support_tunnel - Opens or closes remote support tunnel.
- scale_computing.hypercore.support_tunnel_info - Checks status of the remote support tunnel.
- scale_computing.hypercore.syslog_server - Create, update or delete Syslog servers from HyperCore API.
- scale_computing.hypercore.syslog_server_info - List Syslog servers on HyperCore API
- scale_computing.hypercore.time_server - Modify Time Zone configuration on HyperCore API
- scale_computing.hypercore.time_server_info - List Time Server configuration on HyperCore API.
- scale_computing.hypercore.time_zone - Modify Time Zone configuration on HyperCore API
- scale_computing.hypercore.time_zone_info - List Time Zone configuration on HyperCore API
- scale_computing.hypercore.user - Creates, updates or deletes local hypercore user accounts.
- scale_computing.hypercore.user_info - Returns information about the users.
- scale_computing.hypercore.virtual_disk_info - List DNS configuration on HyperCore API

v1.1.0
======

Release Summary
---------------

Feature release with minor changes and small bugfixes.

Minor Changes
-------------

- Added 'machine_type' option to vm module.
- Added 'source' option to api module.
- Implemented 'put' and added to 'action' option in api module.

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
