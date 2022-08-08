# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# TODO licence

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import env_fallback


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
                no_log=True,
                fallback=(env_fallback, ["SC_TIMEOUT"]),
            ),
        ),
        required_together=[("username", "password")],
    ),
    endpoint=dict(
        type="str",
        required=True,
    ),
    action=dict(
        type="str",
        required=True,
        choices=["post", "patch", "delete", "get", "put"],
    ),
)


def get_spec(*param_names):
    return dict((p, SHARED_SPECS[p]) for p in param_names)
