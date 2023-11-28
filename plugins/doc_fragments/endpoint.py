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
  endpoint:
    description:
      - The raw endpoint that we want to perform post, patch or delete operation on.
    type: str
    required: true
"""
