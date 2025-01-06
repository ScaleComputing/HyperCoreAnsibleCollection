# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # language=yaml
    DOCUMENTATION = r"""
options:
  cloud_init:
    description:
      - Configuration to be used by cloud-init (Linux) or cloudbase-init (Windows).
      - When non-empty will create an extra ISO device attached to VM as a NoCloud datasource.
      - There has to be cloud-config comment present at the beginning of cloud_init file or raw yaml.
      - The cloud-init configuration is applied only during the initial creation of a VM
        (whether through provisioning, cloning, or importing).
        It is not applied to an existing VM.
        This is consistent with the behavior of the HyperCore appliance.
    required: false
    type: dict
    default: {}
    suboptions:
      user_data:
        description:
          - Configuration user-data to be used by cloud-init (Linux) or cloudbase-init (Windows).
          - Valid YAML syntax.
        type: str
      meta_data:
        description:
          - Configuration meta-data to be used by cloud-init (Linux) or cloudbase-init (Windows).
          - Valid YAML syntax.
        type: str
"""
