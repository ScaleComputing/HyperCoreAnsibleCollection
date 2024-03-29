# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.modules import cluster_info
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestRun:
    def test_run(self, rest_client, mocker):
        rest_client.get_record.return_value = dict(
            clusterName="PUB4",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
            icosVersion="9.2.11.210763",
        )

        record = cluster_info.run(rest_client)

        assert record == dict(
            name="PUB4",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
            icos_version="9.2.11.210763",
        )
