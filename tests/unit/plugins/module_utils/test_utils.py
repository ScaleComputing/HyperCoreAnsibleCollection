# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import utils


pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestFilterDict:
    def test_no_field_names(self):
        assert {} == utils.filter_dict(dict(a=1))

    def test_ignoring_none_values(self):
        assert {} == utils.filter_dict(dict(a=None), "a")

    def test_selecting_a_subset_skip_none_values(self):
        assert dict(a=1, c="str") == utils.filter_dict(
            dict(a=1, b=2, c="str", d=None), "a", "c", "d"
        )


class TestTransformAnsibleToHypercoreQuery:
    def test_transform_ansible_to_hypercore_query_ansible_query_empty(self):
        assert {} == utils.transform_ansible_to_hypercore_query(
            dict(),
            dict(vm_name="name"),
        )

    def test_transform_ansible_to_hypercore_query_ansible_success(self):
        assert dict(
            name="demo-vm-name", de="aaa"
        ) == utils.transform_ansible_to_hypercore_query(
            dict(vm_name="demo-vm-name", abc="aaa"),
            dict(vm_name="name", abc="de"),
        )

    def test_transform_ansible_to_hypercore_query_ansible_key_not_found(self):
        with pytest.raises(KeyError):
            utils.transform_ansible_to_hypercore_query(
                dict(vm_name="demo-vm-name"),
                dict(),
            )


class TestGetQuery:
    def test_get_query(self):
        assert {"name": "demo-vm-name"} == utils.get_query(
            dict(vm_name="demo-vm-name", nodes=None),
            "vm_name",
            ansible_hypercore_map=dict(vm_name="name"),
        )
