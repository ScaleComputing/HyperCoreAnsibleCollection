# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  cluster_instance:
    description:
      - Scale Computing HC3 instance information.
    type: dict
    suboptions:
      host:
        description:
          - The HC3 instance url.
          - If not set, the value of the C(SC_URL) environment
            variable will be used.
          - For example "https://10.1.2.3:443".
        required: true
        type: str
      username:
        description:
          - Username used for authentication.
          - If not set, the value of the C(SC_USERNAME) environment
            variable will be used.
        required: true
        type: str
      password:
        description:
          - Password used for authentication.
          - If not set, the value of the C(SC_PASSWORD) environment
            variable will be used.
        required: true
        type: str
      timeout:
        description:
          - Timeout in seconds for the connection with the Scale
            Computing HC3 API instance.
          - If not set, the value of the C(SC_TIMEOUT) environment
            variable will be used.
        required: true
        type: float
"""
