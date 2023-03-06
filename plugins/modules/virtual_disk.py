# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: virtual_disk

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Handles virtual disks on Hypercore cluster.
description:
  - Can create or delete virtual disk on cluster.
  - Creates virtual disk from local disk file.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.virtual_disk_info
options:
  file_location:
    type: str
    description: Location of the disk file.
  file_name:
    type: str
    required: true
    description:
      - Disk file name
      - Hypercore uses this name to identify virtual disk.
      - Can differ from the actual local file name.
  state:
    description:
      - State of the virtual disk.
    choices: [ present, absent]
    type: str
    required: True
"""


EXAMPLES = r"""
- name: upload VD to HyperCore cluster
  scale_computing.hypercore.virtual_disk:
    state: present
    file_name: foobar.qcow2
    file_location: "c:/files/foobar.qcow2"
  register: vd_upload_info

- name: Delete vd from HyperCore cluster
  scale_computing.hypercore.virtual_disk:
    state: absent
    file_name: foobar.qcow2
    file_location: "c:/files/foobar.qcow2"
  register: vd_delete_info
"""

RETURN = r"""
record:
  description:
    - Virtual disk record.
  returned: success
  type: dict
  sample:
    name: foobar.qcow2
    uuid: 57ec1fba-506a-45b9-8950-ffc3dc102c6b
    block_size: 1048576
    size: 104857600
    replication_factor: 2
"""

from ansible.module_utils.basic import AnsibleModule
from typing import Union, Tuple, Optional
import os

from ..module_utils.typed_classes import (
    TypedVirtualDiskToAnsible,
    TypedDiff,
)
from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.utils import is_changed
from ..module_utils.virtual_disk import VirtualDisk
from ..module_utils.state import State

from ..module_utils.hypercore_version import (
    HyperCoreVersion,
)

HYPERCORE_VERSION_REQUIREMENTS = ">=9.2.10"


def read_disk_file(module: AnsibleModule) -> Tuple[bytes, int]:
    file_size = os.path.getsize(module.params["file_location"])
    f = open(module.params["file_location"], "rb")
    content = f.read()
    f.close()
    return content, file_size


def ensure_present(
    module: AnsibleModule,
    rest_client: RestClient,
    virtual_disk_obj: Optional[VirtualDisk],
) -> Tuple[bool, Union[TypedVirtualDiskToAnsible, None], TypedDiff]:
    before = None
    after = None
    if virtual_disk_obj:
        return False, after, dict(before=before, after=after)
    else:
        file_content, file_size = read_disk_file(module)
        VirtualDisk.send_upload_request(
            rest_client, file_content, file_size, module.params["file_name"]
        )
        # No wait_task needed; Upload not returning task ID.
        updated_disk = VirtualDisk.get_by_name(
            rest_client, name=module.params["file_name"], must_exist=True
        )
        after = updated_disk.to_ansible() if updated_disk else None
        return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(
    module: AnsibleModule,
    rest_client: RestClient,
    virtual_disk_obj: Optional[VirtualDisk],
) -> Tuple[bool, Union[TypedVirtualDiskToAnsible, None], TypedDiff]:
    before = None
    after = None
    if not virtual_disk_obj:
        return False, after, dict(before=before, after=after)
    else:
        before = virtual_disk_obj.to_ansible()
        virtual_disk_obj.send_delete_request(rest_client)
        # No wait_task needed; Upload not returning task ID.
        updated_disk = VirtualDisk.get_by_name(
            rest_client, name=module.params["file_name"]
        )
        after = updated_disk.to_ansible() if updated_disk else None
        return is_changed(before, after), after, dict(before=before, after=after)


# Virtual disk can only be created or deleted; No update actions available.
def run(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, Union[TypedVirtualDiskToAnsible, None], TypedDiff]:
    virtual_disk_obj = VirtualDisk.get_by_name(
        rest_client, name=module.params["file_name"]
    )
    if module.params["state"] == State.present:
        return ensure_present(module, rest_client, virtual_disk_obj)
    return ensure_absent(module, rest_client, virtual_disk_obj)


def main() -> None:
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=[
                    "present",
                    "absent",
                ],
                required=True,
            ),
            file_location=dict(
                type="str",
            ),
            file_name=dict(
                type="str",
                required=True,
            ),
        ),
        required_if=[("state", "present", ("file_location",), False)],
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        hcversion = HyperCoreVersion(rest_client)
        if not hcversion.verify(HYPERCORE_VERSION_REQUIREMENTS):
            msg = f"HyperCore server version={hcversion.version} does not match required version {HYPERCORE_VERSION_REQUIREMENTS}"
            module.fail_json(msg=msg)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
