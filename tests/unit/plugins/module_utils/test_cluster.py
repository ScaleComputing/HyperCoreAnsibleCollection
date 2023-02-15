from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.scale_computing.hypercore.plugins.module_utils.cluster import (
    Cluster,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 8), reason="requires python3.8 or higher"
)


class TestCluster:
    def test_cluster_from_hypercore_dict_not_empty(self):
        cluster = Cluster(
            name="PUB4",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
            icos_version="9.2.11.210763",
        )
        hypercore_dict = dict(
            clusterName="PUB4",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
            icosVersion="9.2.11.210763",
        )

        cluster_from_hypercore = Cluster.from_hypercore(hypercore_dict)
        assert cluster == cluster_from_hypercore

    def test_cluster_to_ansible(self):
        cluster = Cluster(
            name="PUB4",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
            icos_version="9.2.11.210763",
        )

        ansible_dict = dict(
            name="PUB4",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
            icos_version="9.2.11.210763",
        )

        assert cluster.to_ansible() == ansible_dict

    def test_cluster_equal_true(self):
        cluster1 = Cluster(
            name="PUB4",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
            icos_version="9.2.11.210763",
        )
        cluster2 = Cluster(
            name="PUB4",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
            icos_version="9.2.11.210763",
        )

        assert cluster1 == cluster2

    def test_cluster_equal_false(self):
        cluster1 = Cluster(
            name="PUB5",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
            icos_version="9.2.11.210763",
        )
        cluster2 = Cluster(
            name="PUB4",
            uuid="f01249a6-2369-4471-bbc2-b4997067b6a6",
            icos_version="9.2.11.210763",
        )

        assert cluster1 != cluster2

    def test_cluster_get(self, rest_client):
        rest_client.get_record.return_value = dict(
            clusterName="PUB4",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
            icosVersion="9.2.11.210763",
        )

        cluster = Cluster.get(rest_client)

        assert cluster == Cluster(
            name="PUB4",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
            icos_version="9.2.11.210763",
        )

    def test_cluster_update_name(self, rest_client):
        name_new = "Updated_name"
        cluster = Cluster(
            name="PUB4",
            uuid="51e6d073-7566-4273-9196-58720117bd7f",
            icos_version="9.2.11.210763",
        )

        cluster.update_name(rest_client, name_new)

        rest_client.update_record.assert_called_with(
            "/rest/v1/Cluster/51e6d073-7566-4273-9196-58720117bd7f",
            {"clusterName": "Updated_name"},
            False,
        )