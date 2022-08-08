# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import enum


# Maybe create enums.py or scale_enums.py and move all enum classes there? @Jure @Justin
class State(str, enum.Enum):
    present = "present"
    absent = "absent"
    set = "set"
