from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: dns_config

author:
  - Ana Zobec (@anazobec)
short_description: Modify DNS configuration on HyperCore API
description:
  - Use this module to add to or delete from a DNS configuration on HyperCore API.
version_added: 1.1.1
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: 
  - module: scale_computing.hypercore.dns_config_info
options:
  overwrite:
    type: str
    choices: [ all, none ]
    default: none
    required: False
    description:
      - The desired way of modifying existing DNS Config entries.
      - If C(all), both searchIPs and searchDomains lists on HyperCore API will be overwritten.
      - If C(none), entries will be updated with new (provided) additional entries.

  search_domains:
    type: list
    elements: dict
    description:
      - Options for modifying the search_domains entry in the DNS configuration.
    suboptions:
      names:
        type: list
        description:
          - List of DNS names to be added or removed from DNS configuration.
          - If the configuration is to be added, then, if all of the provided DNS names already exist on HyperCore API, there will be no changes made.
          - Otherwise, if the configuration is to be removed, and the provided DNS names don't exist on HyperCore API, the plugin will return an error.
      prepend:
        type: bool
        default: False
        description:
          - Choose to prepend or not to the existing config entry.
          - If C(prepend=True), new entry will be I(prepended) to the existing one.
          - If C(prepend=False), new entry will be I(appended) to the existing one.
  dns_servers:
    type: list
    elements: dict
    description:
      - Options for modifying the search_domains entry in the DNS configuration. 
    suboptions:
      ips:
        type: list
        description:
          - List of DNS server IPs to be added or removed from DNS configuration.
          - If the configuration is to be added, then, if all of the provided DNS servers already exist on HyperCore API, there will be no changes made.
          - Otherwise, if the configuration is to be removed, and the provided DNS servers don't exist on HyperCore API, the plugin will return an error.  
      prepend:
        type: bool
        default: False
        description:
          - Same as the I(prepend) option for I(search_domains).
notes:
 - C(check_mode) is not supported.
"""


EXAMPLES = r"""
# Note that only one or both of the config options are required

- name: Add entry to existing DNS configuration
  scale_computing.hypercore.dns_config:
    overwrite: none
    search_domains:
      - names:
          - example.domain1.com
          - example.domain2.com
    dns_servers:
      - ips: 
          - 1.2.3.4
          - 5.6.7.8
        prepend: True

- name: Overwrite all the existing DNS configuration entries
  scale_computing.hypercore.dns_config:
    overwrite: all
    search_domains: 
      - names: []
    dns_servers: 
      - ips: []
"""

RETURN = r"""
results:
  description:
    - Output from modifying entries of the DNS configuration on HyperCore API.
  return: success
  type: list
  sample:
    - uuid: "dnsconfig_guid"
      server_ips:
        - "1.1.1.1"
        - "1.0.0.1"
      search_domains: []
      latest_task_tag:
        completed: 1673966351
        created: 1673966345
        descriptionParameters: []
        formattedDescription: "DNSConfig Update"
        formattedMessage: ""
        messageParameters: []
        modified: 1673966351
        nodeUUIDs:
          - "32c5012d-7d7b-49b4-9201-70e02b0d8758"
        objectUUID: "dnsconfig_guid"
        progressPercent: 100
        sessionID: "b8c45c35-3349-49e0-9474-0edfa73a2162"
        state: "COMPLETE"
        taskTag: "396"
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils.task_tag import TaskTag
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.dns_config import DNSConfig


def modify_dns_config(module, rest_client):
    # GET method, to get the DNS Config by UUID
    dns_config = DNSConfig.get_by_uuid(module.params, rest_client)

    # If DNS config doesn't exist, raise an exception (error)
    if not dns_config:
        raise errors.ScaleComputingError(
            "DNS Config: There is no DNS configuration."
        )

    # Otherwise, continue with modifying the configuration
    before = dns_config.to_ansible()

    # Set the new configurations for dnsServers
    update_dns_servers = before.get("server_ips")
    if module.params["dns_servers"] and module.params["dns_servers"][0]["ips"] is not None:
        if not module.params["dns_servers"][0]["prepend"]:
            update_dns_servers += module.params["dns_servers"][0]["ips"]
        else:
            update_dns_servers = module.params["dns_servers"][0]["ips"] + update_dns_servers

    # Set the new configuration for searchDomains
    update_search_domains = before.get("search_domains")
    if module.params["search_domains"] and module.params["search_domains"][0]["names"] is not None:
        if not module.params["search_domains"][0]["prepend"]:
            update_search_domains += module.params["search_domains"][0]["names"]
        else:
            update_search_domains = module.params["search_domains"][0]["names"] + update_search_domains

    # Remove possible empty string elements from list
    update_dns_servers = list(filter(None, update_dns_servers))
    update_search_domains = list(filter(None, update_search_domains))

    # Check if there will be any changes made to the current configuration
    search_domains_change_needed = dict.fromkeys(update_search_domains) == before.get("search_domains")
    dns_servers_change_needed = dict.fromkeys(update_dns_servers) == before.get("server_ips")

    # When there is no change made, "new_state" then equals "old_state"
    old_state = DNSConfig.get_state(rest_client)
    changed, new_state, diff = (
        not search_domains_change_needed or not dns_servers_change_needed,
        DNSConfig.get_state(rest_client),
        dict(before=old_state, after=old_state),
    )

    # Return no changes made, if there were no
    # changes to be made to the current configuration
    if not changed:
        return changed, new_state, diff

    # 1. Set up the payload and task_tag to modify the current configuration
    # 2. Set up a task to create a new modified record for the configuration
    #    - the update_record method uses method PATCH,
    #    - the create_record method uses method POST.
    # [ NOTE: PUT method is not allowed on DNS Config ]
    task_tag = None
    if module.params["overwrite"] == "none":
        payload = dict(
            searchDomains=update_search_domains,
            serverIPs=update_dns_servers,
        )

        # This method uses PATCH
        # [ NOTE: PUT is not allowed ]
        task_tag = rest_client.update_record(
            endpoint="{0}/{1}".format("/rest/v1/DNSConfig", dns_config.uuid),
            payload=payload,
            check_mode=module.check_mode,
        )
    elif module.params["overwrite"] == "all":
        payload = dict(
            searchDomains=module.params["search_domains"][0]["names"],
            serverIPs=module.params["dns_servers"][0]["ips"],
        )

        # This method uses POST
        # [ NOTE: PUT is not allowed ]
        task_tag = rest_client.create_record(
            endpoint="{0}/{1}".format("/rest/v1/DNSConfig", dns_config.uuid),
            payload=payload,
            check_mode=module.check_mode,
        )

    # Wait for the task to finish
    TaskTag.wait_task(rest_client, task_tag)

    # Get the new configuration and save its new state to then return it
    new_dns_config = DNSConfig.get_by_uuid(module.params, rest_client)
    after = new_dns_config.to_ansible()
    new_state, diff = DNSConfig.get_state(rest_client), dict(before=before, after=after)

    return True, new_state, diff


def run(module, rest_client):
    return modify_dns_config(module, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            # - if "all", both searchIPs and searchDomain lists
            #   on HyperCore API will be overwritten.
            # - if "none" nor searchIPs nor searchDomains lists
            #   will be overwritten, but rather updated with
            #   additional entries.
            overwrite=dict(
                type="str",
                default="none",
                choices=["all", "none"],
                required=False,
            ),
            dns_servers=dict(
                type="list",
                required=False,
                elements="dict",
                options=dict(
                    ips=dict(
                        type="list",
                        required=True,
                    ),
                    # if True, it prepends new values to the beginning
                    # of the list, otherwise it appends to the end of the list.
                    prepend=dict(
                        type="bool",
                        default=False,
                        required=False,
                    ),
                ),
            ),
            search_domains=dict(
                type="list",
                required=False,
                elements="dict",
                options=dict(
                    names=dict(
                        type="list",
                        required=True,
                    ),
                    prepend=dict(
                        type="bool",
                        default=False,
                        required=False,
                    ),
                ),
            ),
        ),
        required_if=[
            ("overwrite", "all", ("dns_servers", "search_domains")),
        ],
    )

    try:
        client = Client(
            host=module.params["cluster_instance"]["host"],
            username=module.params["cluster_instance"]["username"],
            password=module.params["cluster_instance"]["password"],
        )
        rest_client = RestClient(client)
        changed, new_state, diff = run(module, rest_client)
        module.exit_json(changed=changed, new_state=new_state, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
