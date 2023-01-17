from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import PayloadMapper, get_query


class DNSConfig(PayloadMapper):
    def __init__(
        self,
        uuid=None,
        search_domains: [] = None,
        server_ips=None,
        latest_task_tag=None,
    ):
        self.uuid = uuid
        self.search_domains = search_domains if search_domains is not None else []
        self.server_ips = server_ips
        self.latest_task_tag = latest_task_tag if latest_task_tag is not None else {}

    @classmethod
    def from_ansible(cls, dns_config_dict):
        return DNSConfig(
            uuid=dns_config_dict["uuid"],
            search_domains=dns_config_dict["searchDomains"],
            server_ips=dns_config_dict["serverIPs"],
            latest_task_tag=dns_config_dict["latestTaskTag"],
        )

    @classmethod
    def from_hypercore(cls, dns_config_dict):
        if not dns_config_dict:
            return None

        return cls(
            uuid=dns_config_dict["uuid"],
            search_domains=dns_config_dict["searchDomains"],
            server_ips=dns_config_dict["serverIPs"],
            latest_task_tag=dns_config_dict["latestTaskTag"],
        )

    def to_hypercore(self):
        return dict(
            searchDomains=self.search_domains,
            serverIPs=self.server_ips,
        )

    def to_ansible(self):
        return dict(
            uuid=self.uuid,
            search_domains=self.search_domains,
            server_ips=self.server_ips,
            latest_task_tag=self.latest_task_tag,
        )

    # This method is here for testing purposes!
    def __eq__(self, other):
        return all(
            (
                self.uuid == other.uuid,
                self.search_domains == other.search_domains,
                self.server_ips == other.server_ips,
                self.latest_task_tag == other.latest_task_tag,
            )
        )

    @classmethod
    def get_by_uuid(cls, ansible_dict, rest_client, must_exist=False):
        query = get_query(ansible_dict, "uuid", ansible_hypercore_map=dict(uuid="uuid"))
        hypercore_dict = rest_client.get_record(
            "/rest/v1/DNSConfig", query, must_exist=must_exist
        )
        dns_config_from_hypercore = DNSConfig.from_hypercore(hypercore_dict)
        return dns_config_from_hypercore

    @classmethod
    def get_state(cls, rest_client):
        return [
            DNSConfig.from_hypercore(dns_config_dict=hypercore_dict).to_ansible()
            for hypercore_dict in rest_client.list_records("/rest/v1/DNSConfig")
        ]
