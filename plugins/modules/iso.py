#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: iso

author:
  - Tjaž Eržen (@tjazsch)
short_description: Manage ISO images on HyperCore API
description:
  - Use this module to upload a new ISO image from ansible controller to HyperCore or delete existing ISO images from HyperCore API.
  - An ISO image can be uploaded from a shared (SMB) storage or from an HTTP link by downloading it first to the ansible controller's local disk.
version_added: 1.0.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.iso_info
options:
  name:
    type: str
    description:
      - ISO image's name.
      - If ISO object with such name already exists on HyperCore API, no action will be performed.
      - Otherwise, ISO object with such name will be created and iso image from the source uploaded.
    required: true
  state:
    type: str
    description:
      - The desired state of iso object.
      - If I(state=present), the module uploads new ISO image from ansible controller.
      - If I(state=absent), the module deletes an existing ISO image from HyperCore API.
    choices:
      - present
      - absent
    required: true
  source:
    type: str
    description:
      - Only relevant if you want to post an iso image to the HyperCore API (setting C(state=present)).
      - path to ISO image on ansible controller.
      - It must not be http or smb link
notes:
  - C(check_mode) is not supported.
  - Return value C(record) is added in version 1.2.0, and deprecates return value C(results).
    Return value C(results) will be removed in future release.
    R(List of deprecation changes, scale_computing.hypercore.deprecation)
    includes examples to help with transition.
"""


EXAMPLES = r"""
- name: Create ISO image
  scale_computing.hypercore.iso:
    name: CentOS-Stream-9-latest-x86_64-dvd1.iso
    source: /path/to/my.iso  # filename on ansible controller, never http/smb link
    state: present

- name: Remove ISO image
  scale_computing.hypercore.iso:
    name: CentOS-Stream-9-latest-x86_64-dvd1.iso
    state: absent
"""


RETURN = r"""
record:
  description:
    - Updated ISO object from HyperCore API.
  returned: success
  type: dict
  contains:
    mounts:
      description: VMs this image is attached to
      type: list
      elements: dict
      sample:
        vm_uuid: 51e6d073-7566-4273-9196-58720117bd7f
        vm_name: xlab
    name:
      description: Filename of the image, must end in ".iso"
      type: str
      sample: SW_DVD9_Win_Server_STD_CORE_2022_2108.11_64Bit_English_DC_STD_MLF_X23-17134.ISO
    path:
      description: Storage device used in conjunction with VirDomainBlockDevice.path
      type: str
      sample: scribe/171afce9-2452-4294-9bc4-6e8ae49f7e4c
    ready_for_insert:
      description:
        - The flag indicates the ISO image content is fully uploaded, and image is ready to be used.
        - Flag is `false` only for images that are in middle of upload, or where upload was terminated in middle.
      type: bool
      sample: true
    size:
      description: Size of the ISO file, in bytes
      type: int
      sample: 5110759424
    uuid:
      description: Unique identifier
      type: str
      sample: 171afce9-2452-4294-9bc4-6e8ae49f7e4c
results:
  description:
    - List with one element - updated ISO object from HyperCore API.
    - This value is deprecated and will be removed in a future release. Please use record instead.
  returned: success
  type: list
  elements: dict
  contains:
    mounts:
      description: VMs this image is attached to
      type: list
      elements: dict
      sample:
        vm_uuid: 51e6d073-7566-4273-9196-58720117bd7f
        vm_name: xlab
    name:
      description: Filename of the image
      type: str
      sample: SW_DVD9_Win_Server_STD_CORE_2022_2108.11_64Bit_English_DC_STD_MLF_X23-17134.ISO
    path:
      description: Storage device used in conjunction with VirDomainBlockDevice.path
      type: str
      sample: scribe/171afce9-2452-4294-9bc4-6e8ae49f7e4c
    ready_for_insert:
      description:
        - The flag indicates the ISO image content is fully uploaded, and image is ready to be used.
        - Flag is `false` only for images that are in middle of upload, or where upload was terminated in middle.
      type: bool
      sample: true
    size:
      description: Size of the ISO file, in bytes
      type: int
      sample: 5110759424
    uuid:
      description: Unique identifier
      type: str
      sample: 171afce9-2452-4294-9bc4-6e8ae49f7e4c
"""


import os
from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, arguments
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.task_tag import TaskTag
from ..module_utils.iso import ISO

"""
ISO_TIMEOUT_TIME is timeout for ISO data upload.
Currently, assume we have 4.7 GB ISO and speed 1 MB/s -> 4700 seconds.
Rounded to 3600.

TODO: compute it from expected min upload speed and file size.
Even better, try to detect stalled uploads and terminate if no data was transmitted for more than N seconds.
Yum/dnf complain with error "Operation too slow. Less than 1000 bytes/sec transferred the last 30 seconds"
in such case.
"""
ISO_TIMEOUT_TIME = 3600


def ensure_present(module, rest_client):
    iso_image = ISO.get_by_name(module.params, rest_client)
    if iso_image and iso_image.ready_for_insert:
        # ISO object with image uploaded already present, so there is nothing to do
        return False, iso_image.to_ansible(), dict()
    # We need to create and upload ISO
    iso_image = ISO(
        name=module.params["name"],
        size=os.stat(module.params["source"]).st_size,
        ready_for_insert=False,
    )
    task_tag_create = rest_client.create_record(
        "/rest/v1/ISO",
        payload=iso_image.build_iso_post_paylaod(),
        check_mode=False,
    )
    iso_uuid = task_tag_create["createdUUID"]
    TaskTag.wait_task(rest_client, task_tag_create)

    # Uploading ISO image.
    file_size = os.stat(module.params["source"]).st_size
    with open(module.params["source"], "rb") as source_file:
        rest_client.put_record(
            endpoint="/rest/v1/ISO/%s/data" % iso_uuid,
            payload=None,
            check_mode=module.check_mode,
            timeout=ISO_TIMEOUT_TIME,
            binary_data=source_file,
            headers={
                "Content-Type": "application/octet-stream",
                "Accept": "application/json",
                "Content-Length": file_size,
            },
        )

    # Now the ISO image is ready for insertion. Updating readyForInsert to True.
    task_tag_update = rest_client.update_record(
        endpoint="{0}/{1}".format("/rest/v1/ISO", iso_uuid),
        payload=dict(readyForInsert=True),
        check_mode=module.check_mode,
    )
    TaskTag.wait_task(rest_client, task_tag_update)
    iso_image = ISO.get_by_name(module.params, rest_client).to_ansible()
    return True, iso_image, dict(before=None, after=iso_image)


def ensure_absent(module, rest_client):
    iso_image = ISO.get_by_name(module.params, rest_client)
    if iso_image:
        task_tag_delete = rest_client.delete_record(
            endpoint="{0}/{1}".format("/rest/v1/ISO", iso_image.uuid),
            check_mode=module.check_mode,
        )
        TaskTag.wait_task(rest_client, task_tag_delete)
        output = iso_image.to_ansible()
        return True, output, dict(before=output, after=None)
    return False, {}, dict()


def run(module, rest_client):
    if module.params["state"] == "absent":
        return ensure_absent(module, rest_client)
    return ensure_present(module, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(
                type="str",
                required=True,
            ),
            state=dict(
                type="str",
                required=True,
                choices=["present", "absent"],
            ),
            source=dict(
                type="str",
            ),
        ),
        required_if=[
            ("state", "present", ("source",)),
        ],
    )

    module.deprecate(
        "The 'results' return value is being renamed to 'record' and changed from list to dict. "
        "Please use 'record' since 'results' will be removed in future release. "
        "But for now both values are being returned to allow users to migrate their automation.",
        version="3.0.0",
        collection_name="scale_computing.hypercore",
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, results=[record], diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
