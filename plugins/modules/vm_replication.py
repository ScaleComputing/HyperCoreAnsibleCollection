#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_replication

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Plugin handles actions over replications
description:
  - Plugin enables actions over replications on a specified virtual machine
  - Can start, pause and unpause replication on a specified virtual machine
version_added: 0.0.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: []
options:
  state:
    description:
      - State defines which operation should plugin do over selected replication
      - enable, disable, reenable
    choices: [ enabled, disabled, reenabled ]
    type: str
    required: True
  vm_name:
    description:
      - Virtual machine name
      - Used to identify selected virtual machine by name
    type: str
    required: True
  remote_cluster:
    description:
      - remote cluster name
      - Used to identify selected remote cluster by name
    type: str
"""

EXAMPLES = r"""
- name: Replicate demo-vm VM to DC2
  scale_computing.hypercore.vm_replication:
    vm_name: demo-vm
    remote_cluster: PUB4
    state: enabled

- name: Pause replication for demo-vm
  scale_computing.hypercore.vm_replication:
    vm_name: demo-vm
    state: disabled

- name: Reenable replication for demo-vm
  scale_computing.hypercore.vm_replication:
    vm_name: demo-vm
    state: reenabled
"""

RETURN = r"""
record:
  description:
    - The created or changed record for replication on a specified virtual machine.
  returned: success
  type: list
  sample:
    - remote_cluster: "07a2a68a-0afa-4718-9c6f-00a39d08b67e" #TODO: change when cluster_info is implemented
      vm_name: demo-vm
      state: "enabled"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.replication import Replication
from ..module_utils.state import ReplicationState
from ..module_utils.task_tag import TaskTag
from ..module_utils.vm import VM


def ensure_enabled_or_reenabled(module, rest_client):
    changed = False
    before = None
    after = None
    virtual_machine_obj_list = VM.get(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )
    if not virtual_machine_obj_list:
        raise errors.VMNotFound(module.params["vm_name"])
    existing_replication_obj_list = Replication.get(
        rest_client=rest_client,
        query={"sourceDomainUUID": virtual_machine_obj_list[0].uuid},
    )
    if existing_replication_obj_list:  # Update existing
        # TODO: remote_cluster_connection_uuid rename after cluster_info is implemented
        if (
            module.params["remote_cluster"] is None
            or existing_replication_obj_list[0].remote_cluster_connection_uuid
            == module.params["remote_cluster"]
        ) and existing_replication_obj_list[0].state != ReplicationState.enabled:
            before = existing_replication_obj_list[0].to_ansible(
                virtual_machine_obj_list[0]
            )
            existing_replication_obj_list[0].state = ReplicationState.enabled
            data = existing_replication_obj_list[0].to_hypercore()
            rest_client.update_record(
                endpoint="/rest/v1/VirDomainReplication/"
                + existing_replication_obj_list[0].replication_uuid,
                payload=data,
                check_mode=False,
            )
            after = Replication.get(
                rest_client=rest_client,
                query={"sourceDomainUUID": virtual_machine_obj_list[0].uuid},
            )[0].to_ansible(virtual_machine_obj_list[0])
            changed = True
        elif (
            module.params["remote_cluster"] is not None
            and existing_replication_obj_list[0].remote_cluster_connection_uuid
            != module.params["remote_cluster"]
        ):
            raise errors.ReplicationNotUnique(virtual_machine_obj_list[0].name)
    else:  # Create replication
        new_replication_obj = Replication.from_ansible(
            ansible_data=module.params, virtual_machine_obj=virtual_machine_obj_list[0]
        )
        data = new_replication_obj.to_hypercore()
        response = rest_client.create_record(
            endpoint="/rest/v1/VirDomainReplication", payload=data, check_mode=False
        )
        TaskTag.wait_task(rest_client=rest_client, task=response)
        after = Replication.get(
            rest_client=rest_client,
            query={"sourceDomainUUID": virtual_machine_obj_list[0].uuid},
        )[0].to_ansible(virtual_machine_obj_list[0])
        changed = True
    return (
        changed,
        [after],
        dict(before=before, after=after),
    )


def ensure_disabled(module, rest_client):
    changed = False
    after = None
    before = None
    virtual_machine_obj_list = VM.get(
        query={"name": module.params["vm_name"]}, rest_client=rest_client
    )
    if not virtual_machine_obj_list:
        raise errors.VMNotFound(module.params["vm_name"])
    existing_replication_obj_list = Replication.get(
        rest_client=rest_client,
        query={"sourceDomainUUID": virtual_machine_obj_list[0].uuid},
    )
    if (
        existing_replication_obj_list
        and existing_replication_obj_list[0].state != ReplicationState.disabled
    ):
        before = existing_replication_obj_list[0].to_ansible(
            virtual_machine_obj_list[0]
        )
        existing_replication_obj_list[0].state = ReplicationState.disabled
        data = existing_replication_obj_list[0].to_hypercore()
        rest_client.update_record(
            endpoint="/rest/v1/VirDomainReplication/"
            + existing_replication_obj_list[0].replication_uuid,
            payload=data,
            check_mode=False,
        )
        after = Replication.get(
            rest_client=rest_client,
            query={"sourceDomainUUID": virtual_machine_obj_list[0].uuid},
        )[0].to_ansible(virtual_machine_obj_list[0])
        changed = True
    return (changed, [after], dict(before=before, after=after))


def run(module, rest_client):
    if module.params["state"] in [ReplicationState.enabled, ReplicationState.reenabled]:
        return ensure_enabled_or_reenabled(module, rest_client)
    else:
        return ensure_disabled(module, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                required=True,
                choices=["enabled", "disabled", "reenabled"],
            ),
            vm_name=dict(
                type="str",
                required=True,
            ),
            remote_cluster=dict(
                type="str",
            ),
        ),
    )

    try:
        host = module.params["cluster_instance"]["host"]
        username = module.params["cluster_instance"]["username"]
        password = module.params["cluster_instance"]["password"]

        client = Client(host, username, password)
        rest_client = RestClient(client=client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
