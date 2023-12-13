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
  machine_type:
    description:
      - Changes VM machine type.
      - Before this is utilized, a shutdown request is sent.
      - |
        The UEFI machine types require NVRAM disk attached to VM.
        The vTPM machine types require vTPM disk attached to VM.
        If such disk is not present, module will reject machine type change and fail with error.
    type: str
    choices: ["BIOS", "UEFI", "vTPM+UEFI", "vTPM+UEFI-compatible"]
"""
