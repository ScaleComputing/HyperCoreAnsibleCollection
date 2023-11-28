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
  force_reboot:
    description:
      - Can VM be forced to power off and on.
      - Only used when modifications to the VM require it to be powered off
        and VM does not respond to a shutdown request within I(shutdown_timeout) limit.
      - Before this is utilized, a shutdown request is sent.
    type: bool
    default: false
  shutdown_timeout:
    description:
      - How long does ansible controller wait for VMs response to a
        shutdown request.
      - In seconds.
    type: float
    default: 300
"""
