# -*- coding: utf-8 -*-
# # Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils import errors
from ansible_collections.scale_computing.hypercore.plugins.module_utils.smtp import (
    SMTP,
)
from ansible_collections.scale_computing.hypercore.plugins.modules import smtp
from ansible_collections.scale_computing.hypercore.plugins.module_utils.utils import (
    MIN_PYTHON_VERSION,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < MIN_PYTHON_VERSION,
    reason=f"requires python{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher",
)


class TestModifySMTP:
    @pytest.mark.parametrize(
        ("api_entry", "module_entry", "expected"),
        [
            ("a", "a", ("a", False)),
            ("a", "b", ("b", True)),
        ],
    )
    def test_build_entry(self, api_entry, module_entry, expected):
        actual = smtp.build_entry(api_entry, module_entry)
        assert actual == expected

    @pytest.mark.parametrize(
        (
            "description",
            "rc_smtp_server",
            "rc_port",
            "rc_use_ssl",
            "rc_use_auth",
            "rc_auth_user",
            "rc_auth_password",
            "rc_from_address",
            "smtp_server_param",
            "port_param",
            "use_ssl_param",
            "use_auth_param",
            "auth_user_param",
            "auth_password_param",
            "from_address_param",
            "expected_smtp_server",
            "expected_port",
            "expected_use_ssl",
            "expected_use_auth",
            "expected_auth_user",
            "expected_auth_password",
            "expected_from_address",
            "expected_change",
        ),
        [
            (
                # RC
                "desc0",
                "test.com",
                25,
                False,
                True,
                "test",
                "123",
                "test@test.com",
                # PARAMS
                "test.com",
                21,
                False,
                False,
                "",
                "",
                "test@test.com",
                # EXPECTED
                "test.com",
                21,
                False,
                False,
                "",
                "",
                "test@test.com",
                # EXPECTED CHANGE
                True,
            ),
            (
                # RC
                "desc1",
                "test.com",
                25,
                False,
                False,
                "",
                "",
                "",
                # PARAMS
                "test.com",
                21,
                True,
                True,
                "test",
                "123",
                "test@test.com",
                # EXPECTED
                "test.com",
                21,
                True,
                True,
                "test",
                "123",
                "test@test.com",
                # EXPECTED CHANGE
                True,
            ),
            (
                # RC
                "desc2",
                "test.com",
                21,
                False,
                True,
                "test",
                "",  # rc_auth_password
                "test@test.com",
                # PARAMS
                "test.com",
                21,
                False,
                True,
                "test",
                "123",  # auth_password_param
                "test@test.com",
                # EXPECTED
                "test.com",
                21,
                False,
                True,
                "test",
                "123",  # expected_auth_password
                "test@test.com",
                # EXPECTED CHANGE
                True,
            ),
        ],
    )
    def test_modify_smtp_config(
        self,
        description,
        create_module,
        rest_client,
        task_wait,
        mocker,
        rc_smtp_server,
        rc_port,
        rc_use_ssl,
        rc_use_auth,
        rc_auth_user,
        rc_auth_password,
        rc_from_address,
        smtp_server_param,
        port_param,
        use_ssl_param,
        use_auth_param,
        auth_user_param,
        auth_password_param,
        from_address_param,
        expected_smtp_server,
        expected_port,
        expected_use_ssl,
        expected_use_auth,
        expected_auth_user,
        expected_auth_password,
        expected_from_address,
        expected_change,
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0", username="admin", password="admin"
                ),
                server=smtp_server_param,
                port=port_param,
                use_ssl=use_ssl_param,
                use_auth=use_auth_param,
                auth_user=auth_user_param,
                auth_password=auth_password_param,
                from_address=from_address_param,
            )
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.smtp.SMTP.get_by_uuid"
        ).return_value = SMTP(
            uuid="test",
            smtp_server=rc_smtp_server,
            port=rc_port,
            use_ssl=rc_use_ssl,
            use_auth=rc_use_auth,
            auth_user=rc_auth_user,
            auth_password=rc_auth_password,  # password is not returned by API
            from_address=rc_from_address,
            latest_task_tag={},
        )
        mocker.patch(
            "ansible_collections.scale_computing.hypercore.plugins.module_utils.smtp.SMTP.get_state"
        )
        rest_client.create_record.return_value = {
            "taskTag": 123,
        }

        called_with_dict = dict(
            endpoint="/rest/v1/AlertSMTPConfig/test",
            payload=dict(
                smtpServer=expected_smtp_server,
                port=expected_port,
                useSSL=expected_use_ssl,
                authUser=expected_auth_user,
                authPassword=expected_auth_password,
                fromAddress=expected_from_address,
            ),
            check_mode=False,
        )
        smtp.modify_smtp_config(module, rest_client)
        if expected_change:
            rest_client.update_record.assert_called_once_with(**called_with_dict)
        else:
            rest_client.update_record.assert_not_called()

    def test_modify_smtp_config_missing_config(
        self, create_module, rest_client, mocker
    ):
        with pytest.raises(errors.ScaleComputingError):
            module = create_module(
                params=dict(
                    cluster_instance=dict(
                        host="https://0.0.0.0", username="admin", password="admin"
                    ),
                    server="test.com",
                    port=25,
                    use_ssl=True,
                    use_auth=True,
                    auth_user="test",
                    auth_password="123",
                    from_address="test@test.com",
                )
            )
            mocker.patch(
                "ansible_collections.scale_computing.hypercore.plugins.module_utils.smtp.SMTP.get_by_uuid"
            ).return_value = None

            smtp.modify_smtp_config(module, rest_client)


class TestMain:
    def setup_method(self):
        self.cluster_instance = dict(
            host="https://0.0.0.0",
            username="admin",
            password="admin",
        )

    def test_fail(self, run_main):
        success, result = run_main(smtp)

        assert success is False
        assert (
            "missing required arguments: port, server" in result["msg"]
            or "missing required arguments: server, port" in result["msg"]
        )

    def test_required_if(self, run_main):
        params = dict(
            cluster_instance=self.cluster_instance,
            server="test.com",
            port=25,
            use_auth=True,
        )
        success, result = run_main(smtp, params)

        assert success is False
        assert result["msg"]

    @pytest.mark.parametrize(
        (
            "server",
            "port",
            "use_ssl",
            "use_auth",
            "auth_user",
            "auth_password",
            "from_address",
        ),
        [
            (
                "test.com",
                25,
                True,
                True,
                "test",
                "123",
                "test@test.com",
            ),
            (
                "test.com",
                25,
                None,
                None,
                None,
                None,
                None,
            ),
            (
                "test.com",
                25,
                False,
                False,
                None,
                None,
                "test@test.com",
            ),
        ],
    )
    def test_params(
        self,
        run_main,
        server,
        port,
        use_ssl,
        use_auth,
        auth_user,
        auth_password,
        from_address,
    ):
        params = dict(
            cluster_instance=self.cluster_instance,
            server=server,
            port=port,
            use_auth=use_auth,
            auth_user=auth_user,
            auth_password=auth_password,
            from_address=from_address,
        )
        success, result = run_main(smtp, params)

        assert success is True
