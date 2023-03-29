# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from typing import Optional

FROM_HYPERCORE_TO_ANSIBLE_NIC_TYPE = {
    None: None,
    "RTL8139": "RTL8139",
    "VIRTIO": "virtio",
    "INTEL_E1000": "INTEL_E1000",
}
FROM_ANSIBLE_TO_HYPERCORE_NIC_TYPE = {
    v: k for k, v in FROM_HYPERCORE_TO_ANSIBLE_NIC_TYPE.items()
}


# Maybe create enums.py or scale_enums.py and move all enum classes there? @Jure @Justin
class NicType:
    @classmethod
    def ansible_to_hypercore(cls, ansible_value: Optional[str]) -> Optional[str]:
        return FROM_ANSIBLE_TO_HYPERCORE_NIC_TYPE[ansible_value]

    @classmethod
    def hypercore_to_ansible(cls, hypercore_value: str) -> Optional[str]:
        return FROM_HYPERCORE_TO_ANSIBLE_NIC_TYPE[hypercore_value]
