# Ansible Collection for Scale Computing HyperCore

The Ansible Collection for Scale Computing HyperCore ([HyperCore](https://www.scalecomputing.com/sc-hypercore))
a variety of Ansible content to help automate the management of Scale Computing HyperCore products.


<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.12**.

The collection should work with any Ansible version **>=2.9.10**,
but this is not granted.
<!--end requires_ansible-->

## Python version compatibility

This collection requires Python 3.8 or greater.

## HyperCore cluster API version compatibility

This collection has been tested against HyperCore cluster API version v9.1.14.208456.

## Included content

### Inventory plugins

<!--start html content-->

   <style type="text/css">
   .tg  {border-collapse:collapse;border-spacing:0;}
   .tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
   overflow:hidden;padding:10px 5px;word-break:normal;}
   .tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
   font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
   .tg .tg-cjtp{background-color:#ecf4ff;border-color:inherit;text-align:left;vertical-align:top}
   .tg .tg-6e8n{background-color:#c0c0c0;border-color:inherit;font-weight:bold;text-align:left;vertical-align:top}
   .tg .tg-fymr{border-color:inherit;font-weight:bold;text-align:left;vertical-align:top}
   .tg .tg-0pky{border-color:inherit;text-align:left;vertical-align:top}
   .tg .tg-fgdu{background-color:#ecf4ff;border-color:inherit;font-weight:bold;text-align:left;vertical-align:top}
   </style>
   <table class="tg">
   <thead>
   <tr>
      <th class="tg-6e8n">Module name</th>
      <th class="tg-6e8n">Description</th>
   </tr>
   </thead>
   <tbody>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.hypercore</td>
      <td class="tg-0pky">Inventory source to list HyperCore Virtual Machines.</td>
   </tr>
   </tbody>
   </table>

<!--end html content-->

### Modules

<!--start html content-->

   <style type="text/css">
   .tg  {border-collapse:collapse;border-spacing:0;}
   .tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
   overflow:hidden;padding:10px 5px;word-break:normal;}
   .tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
   font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
   .tg .tg-cjtp{background-color:#ecf4ff;border-color:inherit;text-align:left;vertical-align:top}
   .tg .tg-6e8n{background-color:#c0c0c0;border-color:inherit;font-weight:bold;text-align:left;vertical-align:top}
   .tg .tg-fymr{border-color:inherit;font-weight:bold;text-align:left;vertical-align:top}
   .tg .tg-0pky{border-color:inherit;text-align:left;vertical-align:top}
   .tg .tg-fgdu{background-color:#ecf4ff;border-color:inherit;font-weight:bold;text-align:left;vertical-align:top}
   </style>
   <table class="tg">
   <thead>
   <tr>
      <th class="tg-6e8n">Module name</th>
      <th class="tg-6e8n">Description</th>
   </tr>
   </thead>
   <tbody>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.vm</td>
      <td class="tg-0pky">Create, update or delete a virtual machine.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.vm_info</td>
      <td class="tg-cjtp">Get information about existing virtual machines.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.vm_params</td>
      <td class="tg-0pky">Partialy update a virtual machine. Use when changing some of the properties of an existing VM.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.vm_disk</td>
      <td class="tg-cjtp">Update block devices on VM.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.vm_nic</td>
      <td class="tg-0pky">Update network interfaces (NICs) on a VM.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.vm_boot_devices</td>
      <td class="tg-cjtp">Set up a boot order for the specified VM.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.vm_node_affinity</td>
      <td class="tg-0pky">Set up node affinity for a specified VM.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.node_info</td>
      <td class="tg-cjtp">Get the list of all nodes on a cluster. Needed to set node affinities for VMs.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.remote_cluster_info</td>
      <td class="tg-0pky">Get Information regarding remote replication clusters.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.vm_replication</td>
      <td class="tg-cjtp">Configure a VM replication.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.vm_replication_info</td>
      <td class="tg-0pky">Get a VM replication configuration.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.snapshot_schedule</td>
      <td class="tg-cjtp">Configure a snapshot schedule.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.snapshot_schedule_info</td>
      <td class="tg-0pky">Get the existing list of snapshot schedules.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.iso</td>
      <td class="tg-cjtp">Upload a new ISO image, or edit an existing one.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.iso_info</td>
      <td class="tg-0pky">Get a list of available ISO images.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.api</td>
      <td class="tg-cjtp">Use to directly access to HyperCore API.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.vm_export</td>
      <td class="tg-0pky">Export a VM to an SMB server. </td>
   </tr>
   <tr>
      <td class="tg-fgdu">scale_computing.hypercore.vm_import</td>
      <td class="tg-cjtp">Import a VM from an SMB or an HTTP URI.</td>
   </tr>
   <tr>
      <td class="tg-fymr">scale_computing.hypercore.vm_clone</td>
      <td class="tg-0pky">Clone a VM.</td>
   </tr>
   </tbody>
   </table>

<!--end html content-->



# Examples

The [examples](https://github.com/ScaleComputing/HyperCoreAnsibleCollection/tree/main/examples)
subdirectory contains usage examples for individual modules.
Look at [examples/README.md](https://github.com/ScaleComputing/HyperCoreAnsibleCollection/tree/main/examples/README.md) to see how to use each example.

# Development

See [DEVELOPMENT.md](https://github.com/ScaleComputing/HyperCoreAnsibleCollection/tree/main/DEVELOPMENT.md).
