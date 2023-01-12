from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.task_tag import TaskTag
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.dns_config import DNSConfig


def ensure_present(module, rest_client):
    dns_config = DNSConfig.get_by_uuid(module.params, rest_client)
    before = dns_config.to_ansible()

    create_dns_servers = (
        before.get("server_ips")
        if module.params["dns_servers"] is None
        else list(
            dict.fromkeys(before.get("server_ips") + module.params["dns_servers"])
        )
    )
    create_search_domains = (
        before.get("search_domains")
        if module.params["search_domains"] is None
        else list(
            dict.fromkeys(
                before.get("search_domains") + module.params["search_domains"]
            )
        )
    )

    # remove possible empty string elements from list
    create_dns_servers = list(filter(None, create_dns_servers))
    create_search_domains = list(filter(None, create_search_domains))

    unchanged_search_domains = create_search_domains == before.get("search_domains")
    unchanged_dns_servers = create_dns_servers == before.get("server_ips")
    changed, result, _dict = (
        not unchanged_search_domains or not unchanged_dns_servers,
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


def ensure_absent(module, rest_client):  # delete
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
    # return False, [], dict()


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
            ),
            search_domains=dict(type="list", required=False),
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
