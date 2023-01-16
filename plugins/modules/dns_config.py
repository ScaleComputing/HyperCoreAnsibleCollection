from __future__ import absolute_import, division, print_function

__metaclass__ = type

# language=yaml
DOCUMENTATION = r"""
module: dns_config

author:
  - Ana Zobec (@anazobec)
short_description: Modify DNS configuration on HyperCore API
description:
  - Use this module to add to or delete from a DNS configuration on HyperCore API.
version_added: 1.1.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso: 
  - module: scale_computing.hypercore.dns_config_info
options:
  search_domains:
    type: list
    description:
      - List of DNS names to be added or removed from DNS configuration.
      - If the configuration is to be added, then, if all of the provided DNS names already exist on HyperCore API, there will be no changes made.
      - Otherwise, if the configuration is to be removed, and the provided DNS names don't exist on HyperCore API, the plugin will return an error.
  dns_servers:
    type: list
    description:
      - List of DNS server IPs to be added or removed from DNS configuration.
      - If the configuration is to be added, then, if all of the provided DNS servers already exist on HyperCore API, there will be no changes made.
      - Otherwise, if the configuration is to be removed, and the provided DNS servers don't exist on HyperCore API, the plugin will return an error.  
  state:
    type: str
    description:
      - The desired state of DNS configuration object.
      - You must provide one or both of the DNS configuration lists - search_domains and dns_servers.
      - If I(state=present), the module modifies the desired DNS configuration on HyperCore API.
      - If I(state=absent), the module removes the desired DNS configuration on HyperCore API.
    choices: 
      - present
      - absent
    required: true
notes:
 - C(check_mode) is not supported.
"""

# language=yaml
EXAMPLES = r"""
# Note that only one or both of the config options are required

- name: Add/modify a DNS configuration
  scale_computing.hypercore.dns_config:
    search_domains:
      - "example.domain.com"
      - "example.domain123.com"
    dns_servers: 
      - "1.2.3.4"
      - "5.6.7.8"
      - "9.10.11.12"
    state: present

- name: Delete a DNS configuration
  scale_computing.hypercore.dns_config:
    search_domains:
      - "example.domain123.com"
    dns_servers:
      - "9.10.11.12"
    state: absent
"""

# language=yaml
RETURN = r"""
results:
  description:
    - Updated the DNS configuration on HyperCore API.
  return: success
  type: dict
  
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils.task_tag import TaskTag
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.dns_config import DNSConfig


def get_dns_config_info(module, rest_client):
    return [
        DNSConfig.from_hypercore(dns_config_dict=hypercore_dict).to_ansible()
        for hypercore_dict in rest_client.list_records("/rest/v1/DNSConfig")
    ]


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
    if module.params["dns_servers"][0]["ips"] is not None:
        if not module.params["dns_servers"][0]["prepend"]:
            update_dns_servers += module.params["dns_servers"][0]["ips"]
        else:
            update_dns_servers = module.params["dns_servers"][0]["ips"] + update_dns_servers

    # Set the new configuration for searchDomains
    update_search_domains = before.get("search_domains")
    if module.params["search_domains"][0]["names"] is not None:
        if not module.params["search_domains"][0]["prepend"]:
            update_search_domains += module.params["search_domains"][0]["names"]
        else:
            update_search_domains = module.params["search_domains"][0]["names"] + update_search_domains

    # Remove possible empty string elements from list
    update_dns_servers = list(filter(None, update_dns_servers))
    update_search_domains = list(filter(None, update_search_domains))

    # Check if there will be any changes made to the current configuration
    search_domains_change_needed = update_search_domains == before.get("search_domains")
    dns_servers_change_needed = update_dns_servers == before.get("server_ips")

    # When there is no change made, "new_state" then equals "old_state"
    old_state = get_dns_config_info(module, rest_client)
    module.warn(str(old_state))
    changed, new_state, diff = (
        not search_domains_change_needed or not dns_servers_change_needed,
        get_dns_config_info(module, rest_client),
        dict(before=old_state, after=old_state),
    )

    # Return no changes made, if there were no
    # changes to be made to the current configuration
    if not changed:
        return changed, new_state, diff

    # Set up the new (modified) configuration
    dns_config_update = DNSConfig(
        search_domains=update_search_domains,
        server_ips=update_dns_servers,
    )

    # Set up the payload to modify the current configuration
    # TODO: use GET method to build payload!
    payload = DNSConfig.to_hypercore(dns_config_update)

    # Set up a task to create a new modified record for the configuration
    # the update_record method uses method PATCH
    # NOTE: PUT method is not allowed on DNS Config
    task_tag_update = rest_client.update_record(
        endpoint="{0}/{1}".format("/rest/v1/DNSConfig", dns_config.uuid),
        payload=payload,
        check_mode=module.check_mode,
    )

    # Wait for the task to finish
    TaskTag.wait_task(rest_client, task_tag_update)

    # Get the new configuration and save its new state to then return it
    new_dns_config = DNSConfig.get_by_uuid(module.params, rest_client)
    after = new_dns_config.to_ansible()
    new_state, diff = get_dns_config_info(module, rest_client), dict(before=before, after=after)

    return True, new_state, diff


def run(module, rest_client):
    return modify_dns_config(module, rest_client)


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
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
