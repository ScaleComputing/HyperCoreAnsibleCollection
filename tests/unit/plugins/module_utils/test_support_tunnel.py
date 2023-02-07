# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.support_tunnel import (
    SupportTunnel,
)
from ansible_collections.scale_computing.hypercore.plugins.module_utils.client import (
    Response,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestSupportTunnel:
    def test_support_tunnel_from_hypercore(self):
        support_tunnel = SupportTunnel(
            open=True,
            code=4422,
        )

        hypercore_dict = dict(
            tunnelOpen=4422,
        )

        support_tunnel_from_hypercore = SupportTunnel.from_hypercore(hypercore_dict)
        assert support_tunnel == support_tunnel_from_hypercore

    def test_support_tunnel_from_hypercore_false(self):
        support_tunnel = SupportTunnel(
            open=False,
            code=None,
        )

        hypercore_dict = dict(
            tunnelOpen=False,
        )

        support_tunnel_from_hypercore = SupportTunnel.from_hypercore(hypercore_dict)
        assert support_tunnel == support_tunnel_from_hypercore

    def test_support_tunnel_to_ansible(self):
        support_tunnel = SupportTunnel(open=True, code=4422)

        ansible_dict = dict(open=True, code=4422)

        assert support_tunnel.to_ansible() == ansible_dict

    def test_support_tunnel_equal_true(self):
        support_tunnel1 = SupportTunnel(open=True, code=4422)
        support_tunnel2 = SupportTunnel(open=True, code=4422)

        assert support_tunnel1 == support_tunnel2

    def test_support_tunnel_equal_false(self):
        support_tunnel1 = SupportTunnel(open=True, code=4422)
        support_tunnel2 = SupportTunnel(open=False, code=None)

        assert support_tunnel1 != support_tunnel2

    def test_check_tunnel_status(self, client):
        client.get.return_value = Response(status=200, data='{ "tunnelOpen": 20503 }')

        tunnel_status = SupportTunnel.check_tunnel_status(client)

        client.get.assert_called_with("/support-api/check")
        assert tunnel_status.open is True
        assert tunnel_status.code == 20503

    def test_check_tunnel_status_false(self, client):
        client.get.return_value = Response(status=200, data='{ "tunnelOpen": false }')

        tunnel_status = SupportTunnel.check_tunnel_status(client)

        client.get.assert_called_with("/support-api/check")
        assert tunnel_status.open is False
        assert tunnel_status.code is None

    def test_open_tunnel(self, create_module, client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    username=None,
                    password=None,
                ),
                status="present",
                code=4422,
            ),
        )
        client.get.return_value = Response(status=200, data="")

        SupportTunnel.open_tunnel(module, client)

        client.get.assert_called_with("/support-api/open", query={"code": 4422})

    def test_close_tunnel(self, client):
        client.get.return_value = Response(status=200, data="")
        SupportTunnel.close_tunnel(client)

        client.get.assert_called_with("/support-api/close")
