from __future__ import absolute_import, division, print_function

__metaclass__ = type


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


def ensure_present(module, rest_client):
    dns_config = DNSConfig.get_by_uuid(module.params, rest_client)
    if not dns_config:
        raise errors.ScaleComputingError(
            f"DNS config: There is no DNS configuration."
        )

    before = dns_config.to_ansible()

    create_dns_servers = \
        before.get("server_ips") \
        if module.params["dns_servers"] is None \
        else dict.fromkeys(before.get("server_ips") + module.params["dns_servers"])

    create_search_domains = \
        before.get("search_domains") \
        if module.params["search_domains"] is None \
        else before.get("search_domains") + module.params["search_domains"]

    # remove possible empty string elements from list
    create_dns_servers = list(filter(None, create_dns_servers))
    create_search_domains = list(filter(None, create_search_domains))

    search_domains_change_needed = create_search_domains == before.get("search_domains")
    dns_servers_change_needed = create_dns_servers == before.get("server_ips")
    changed, result, _dict = (
        not search_domains_change_needed or not dns_servers_change_needed,
        [],
        dict(),
    )

    if not changed:
        return changed, result, _dict

    dns_config_create = DNSConfig(
        search_domains=create_search_domains,
        server_ips=create_dns_servers,
    )

    payload = DNSConfig.to_hypercore(dns_config_create)

    task_tag_create = rest_client.create_record(
        endpoint="{0}/{1}".format("/rest/v1/DNSConfig", dns_config.uuid),
        payload=payload,
        check_mode=module.check_mode,
    )

    TaskTag.wait_task(rest_client, task_tag_create)
    new_dns_config = DNSConfig.get_by_uuid(module.params, rest_client)
    after = new_dns_config.to_ansible()
    changed, result, _dict = before != after, [after], dict(before=before, after=after)

    return changed, result, _dict


# TODO: remove ensure_absent method
def ensure_absent(module, rest_client):  # remove items from lists: dnsServers, searchDomains
    dns_config = DNSConfig.get_by_uuid(module.params, rest_client)
    before = dns_config.to_ansible()

    delete_dns_servers = (
        [] if module.params["dns_servers"] is None else module.params["dns_servers"]
    )
    delete_search_domains = (
        []
        if module.params["search_domains"] is None
        else module.params["search_domains"]
    )

    new_dns_servers = [el for el in before.get("server_ips")]
    new_search_domains = [el for el in before.get("search_domains")]

    for delete_dns_server in delete_dns_servers:
        try:
            new_dns_servers.remove(delete_dns_server)
        except ValueError:
            raise errors.ScaleComputingError(
                f"DNS config: IP '{delete_dns_server}' doesn't exist in DNS config records."
            )
    for delete_search_domain in delete_search_domains:
        try:
            new_search_domains.remove(delete_search_domain)
        except ValueError:
            raise errors.ScaleComputingError(
                f"DNS config: Search domain name '{delete_search_domain}' doesn't exist in DNS config records."
            )

    dns_config_new = DNSConfig(
        search_domains=new_search_domains,
        server_ips=new_dns_servers,
    )
    payload = DNSConfig.to_hypercore(dns_config_new)
    task_tag_create = rest_client.create_record(
        endpoint="{0}/{1}".format("/rest/v1/DNSConfig", dns_config.uuid),
        payload=payload,
        check_mode=module.check_mode,
    )
    TaskTag.wait_task(rest_client, task_tag_create)
    new_dns_config = DNSConfig.get_by_uuid(module.params, rest_client)
    after = new_dns_config.to_ansible()
    return before != after, [after], dict(before=before, after=after)


def run(module, rest_client):
    if module.params["state"] == "absent":
        return ensure_absent(module, rest_client)
    return ensure_present(module, rest_client)


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
                    # if True, it prepends new values to the beginning
                    # of the list, otherwise it appends to the end of the list.
                    prepend=dict(
                        type="bool",
                        default=False,
                        required=False
                    ),
                ),
            ),
            search_domains=dict(
                type="list",
                required=False
            ),
            state=dict(
                type="str",
                required=True,
                choices=["present", "absent"],
            ),
        ),
        required_one_of=[
            (
                "state",
                "present",
                (
                    "dns_servers",
                    "search_domains",
                ),
            ),
            (
                "state",
                "absent",
                (
                    "dns_servers",
                    "search_domains",
                ),
            ),
        ],
    )

    try:
        client = Client(
            host=module.params["cluster_instance"]["host"],
            username=module.params["cluster_instance"]["username"],
            password=module.params["cluster_instance"]["password"],
        )
        rest_client = RestClient(client)
        changed, results, diff = run(module, rest_client)
        module.exit_json(changed=changed, results=results, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
