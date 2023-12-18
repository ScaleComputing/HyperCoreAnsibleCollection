# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from __future__ import annotations

__metaclass__ = type

from ansible.module_utils.basic import env_fallback
from typing import Any
from ..module_utils.client import AuthMethod

# TODO - env from /etc/environment is loaded
# But when env is set in bash session, env seems to be lost on ssh connection to localhost.
# connection=local might help, but only for localhost.
# Maybe: set variables via inventory, or extra-vars.

SHARED_SPECS = dict(
    cluster_instance=dict(
        type="dict",
        apply_defaults=True,
        options=dict(
            host=dict(
                type="str",
                required=True,
                fallback=(env_fallback, ["SC_HOST"]),
            ),
            username=dict(
                type="str",
                required=True,
                fallback=(env_fallback, ["SC_USERNAME"]),
            ),
            password=dict(
                type="str",
                required=True,
                no_log=True,
                fallback=(env_fallback, ["SC_PASSWORD"]),
            ),
            timeout=dict(
                type="float",
                required=False,
                fallback=(env_fallback, ["SC_TIMEOUT"]),
            ),
            auth_method=dict(
                type="str",
                default=AuthMethod.local,
                choices=[am.value for am in AuthMethod],
                fallback=(env_fallback, ["SC_AUTH_METHOD"]),
            ),
        ),
        required_together=[("username", "password")],
    ),
    machine_type=dict(
        type="str",
        choices=["BIOS", "UEFI", "vTPM+UEFI", "vTPM+UEFI-compatible"],
    ),
)


def get_spec(*param_names: str) -> dict[Any, Any]:
    return dict((p, SHARED_SPECS[p]) for p in param_names)
