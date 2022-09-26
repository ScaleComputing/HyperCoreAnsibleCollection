Scale Computing Hypercore Ansible collection
============================================

Official Ansible collection for Scale Computing HyperCore (HC3) v1 API.

.. raw:: html

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
      <th class="tg-6e8n">module name</th>
      <th class="tg-6e8n">Description</th>
   </tr>
   </thead>
   <tbody>
   <tr>
      <td class="tg-fymr">vm</td>
      <td class="tg-0pky">Create, update or delete a virtual machine.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">vm_info</td>
      <td class="tg-cjtp">Get information about existing virtual machines.</td>
   </tr>
   <tr>
      <td class="tg-fymr">vm_params</td>
      <td class="tg-0pky">Partialy update a virtual machine. Use when changing some of the properties of an existing VM.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">vm_disk</td>
      <td class="tg-cjtp">Update block devices on VM.</td>
   </tr>
   <tr>
      <td class="tg-fymr">vm_nic</td>
      <td class="tg-0pky">Update network interfaces (NICs) on a VM.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">vm_boot_devices</td>
      <td class="tg-cjtp">Set up a boot order for the specified VM.</td>
   </tr>
   <tr>
      <td class="tg-fymr">vm_node_affinity</td>
      <td class="tg-0pky">Set up node affinity for a specified VM.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">node_info</td>
      <td class="tg-cjtp">Get the list of all nodes on a cluster. Needed to set node affinities for VMs.</td>
   </tr>
   <tr>
      <td class="tg-fymr">remote_cluster_info</td>
      <td class="tg-0pky">Get Information regarding remote replication clusters.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">vm_replication</td>
      <td class="tg-cjtp">Configure a VM replication.</td>
   </tr>
   <tr>
      <td class="tg-fymr">vm_replication_info</td>
      <td class="tg-0pky">Get a VM replication configuration.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">snapshot_schedule</td>
      <td class="tg-cjtp">Configure a snapshot schedule.</td>
   </tr>
   <tr>
      <td class="tg-fymr">snapshot_schedule_info</td>
      <td class="tg-0pky">Get the existing list of snapshot schedules.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">iso</td>
      <td class="tg-cjtp">Upload a new ISO image, or edit an existing one.</td>
   </tr>
   <tr>
      <td class="tg-fymr">iso_info</td>
      <td class="tg-0pky">Get a list of available ISO images.</td>
   </tr>
   <tr>
      <td class="tg-fgdu">api</td>
      <td class="tg-cjtp">Use to directly access to HyperCore API.</td>
   </tr>
   <tr>
      <td class="tg-fymr">vm_export</td>
      <td class="tg-0pky">Export a VM to an SMB server. </td>
   </tr>
   <tr>
      <td class="tg-fgdu">vm_import</td>
      <td class="tg-cjtp">Import a VM from an SMB or an HTTP URI.</td>
   </tr>
   <tr>
      <td class="tg-fymr">vm_clone</td>
      <td class="tg-0pky">Clone a VM.</td>
   </tr>
   </tbody>
   </table>
   <br>Tested on HyperCore API version v9.1.14.208456.
   <br><br>


.. toctree::
   :maxdepth: 2
   :caption: Scale Computing Hypercore Ansible collection

   quickstart
   installation


.. toctree::
   :maxdepth: 1
   :caption: References

   roles
   modules
