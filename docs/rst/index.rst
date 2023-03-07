
.. _docsite_root_index:

Welcome to Scale Computing HyperCore Ansible Collection documentation
=====================================================================

This docsite contains documentation of scale_computing.hypercore,
official Ansible Collection for Scale Computing HyperCore (HC3) v1 API.

While different modules perform different tasks, their interfaces all follow the same pattern as much as possible.
For instance, all Hypercore action modules do not support ``check_mode``,
most of them can have their state set to either ``present`` or ``absent``,
and they identify the resource to operate by using the ``name`` (or equivalent) parameter.

The API of each module is composed of two parts.
The ``cluster_instance`` parameter contains the authentication information
that are related to the HyperCore backend that the module is connecting to.
All other parameters hold the information related to the resource that we are operating on.

.. toctree::
   :maxdepth: 2
   :caption: Collections:

   collections/index


.. toctree::
   :maxdepth: 1
   :caption: Plugin indexes:
   :glob:

   collections/index_*


.. toctree::
   :maxdepth: 1
   :caption: Reference indexes:

   collections/environment_variables

Tested on HyperCore API version v9.1.14.208456.
