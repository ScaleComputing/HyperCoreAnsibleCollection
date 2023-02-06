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
from ansible_collections.scale_computing.hypercore.plugins.module_utils.errors import (
    UnexpectedAPIResponse,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestSupportTunnel:
    def test_support_tunnel_from_hypercore(self):
        support_tunnel = SupportTunnel(
            tunnel_open=4422,
        )

        hypercore_dict = dict(
            tunnelOpen=4422,
        )

        support_tunnel_from_hypercore = SupportTunnel.from_hypercore(hypercore_dict)
        assert support_tunnel == support_tunnel_from_hypercore

    def test_support_tunnel_to_ansible(self):
        support_tunnel = SupportTunnel(tunnel_open=4422)

        ansible_dict = dict(tunnel_open=4422)

        assert support_tunnel.to_ansible() == ansible_dict

    def test_user_equal_true(self):
        support_tunnel1 = SupportTunnel(tunnel_open=4422)
        support_tunnel2 = SupportTunnel(tunnel_open=4422)

        assert support_tunnel1 == support_tunnel2

    def test_user_equal_false(self):
        support_tunnel1 = SupportTunnel(tunnel_open=4422)
        support_tunnel2 = SupportTunnel(tunnel_open=3355)

        assert support_tunnel1 != support_tunnel2

    def test_check_tunnel_status(self, client):
        client.get.return_value = Response(status=200, data='{ "tunnelOpen": 20503 }')

        tunnel_status = SupportTunnel.check_tunnel_status(client)

        client.get.assert_called_with("/support-api/check")
        assert tunnel_status.tunnel_open == 20503

    def test_check_tunnel_status_404(self, client):
        client.get.return_value = Response(status=404, data="")

        with pytest.raises(UnexpectedAPIResponse) as exc:
            SupportTunnel.check_tunnel_status(client)
        assert "Unexpected response - 404" in str(exc.value)

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

    def test_open_tunnel_404(self, create_module, client):
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
        client.get.return_value = Response(status=404, data="")

        with pytest.raises(UnexpectedAPIResponse) as exc:
            SupportTunnel.open_tunnel(module, client)
        assert "Unexpected response - 404" in str(exc.value)

    def test_close_tunnel(self, client):
        client.get.return_value = Response(status=200, data="")
        SupportTunnel.close_tunnel(client)

        client.get.assert_called_with("/support-api/close")

    def test_close_tunnel_404(self, client):
        client.get.return_value = Response(status=404, data="")

        with pytest.raises(UnexpectedAPIResponse) as exc:
            SupportTunnel.close_tunnel(client)
        assert "Unexpected response - 404" in str(exc.value)
