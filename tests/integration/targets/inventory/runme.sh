#!/usr/bin/env bash

readonly vars_file=../../integration_config.yml

eval "$(cat <<EOF | python
import yaml
with open("$vars_file") as fd:
    data = yaml.safe_load(fd)
sc_host=data["sc_host"]
sc_timeout=data["sc_timeout"]
print("export SC_HOST='{}'".format(sc_host))
print("export SC_TIMEOUT='{}'".format(sc_timeout))
print("export SC_USERNAME='{}'".format(data["sc_config"][sc_host]["sc_username"]))
print("export SC_PASSWORD='{}'".format(data["sc_config"][sc_host]["sc_password"]))
# SC_AUTH_METHOD==local by default, leave it unset
EOF
)"

env | grep SC_

set -eux

# Inject hypercore_inventory.yml with needed values before running tests
# Use examples/hypercore_inventory.yml as template.
# cat file to fail early if hypercore_inventory.yml is missing.
cat "$(dirname "$(realpath "$0")")/hypercore_inventory_ansible_enable.yml"
cat "$(dirname "$(realpath "$0")")/hypercore_inventory_ansible_disable.yml"
cat "$(dirname "$(realpath "$0")")/hypercore_inventory_ansible_both_true.yml"
cat "$(dirname "$(realpath "$0")")/hypercore_inventory_ansible_both_false.yml"


export ANSIBLE_PYTHON_INTERPRETER="$ANSIBLE_TEST_PYTHON_INTERPRETER"

function cleanup {
    unset ANSIBLE_CACHE_PLUGIN
    unset ANSIBLE_CACHE_PLUGIN_CONNECTION
}

trap 'cleanup "$@"' EXIT


ansible-playbook cleanup.yml
ansible-playbook prepare.yml

ansible-playbook -i localhost, -i hypercore_inventory_ansible_enable.yml run_ansible_enable_tests.yml
ansible-playbook -i localhost, -i hypercore_inventory_ansible_disable.yml run_ansible_disable_tests.yml
ansible-playbook -i localhost, -i hypercore_inventory_ansible_both_true.yml run_ansible_both_true_tests.yml

# do one test without SC_TIMEOUT
unset SC_TIMEOUT
ansible-playbook -i localhost, -i hypercore_inventory_ansible_both_false.yml run_ansible_both_false_tests.yml
# test with SC_AUTH_METHOD being set to "local"
export SC_AUTH_METHOD=local
ansible-playbook -i localhost, -i hypercore_inventory_ansible_both_false.yml run_ansible_both_false_tests.yml

# test with OIDC user
# We can do this only if OIDC login is configured.
echo "Testing inventory plugin with OIDC user."
eval "$(cat <<EOF | python
import yaml
with open("$vars_file") as fd:
    data = yaml.safe_load(fd)
sc_host=data["sc_host"]
sc_timeout=data["sc_timeout"]
print("export SC_HOST='{}'".format(sc_host))
print("export SC_TIMEOUT='{}'".format(sc_timeout))
print("export SC_USERNAME='{}'".format(data["sc_config"][sc_host]["oidc"]["users"][0]["username"]))
print("export SC_PASSWORD='{}'".format(data["sc_config"][sc_host]["oidc"]["users"][0]["password"]))
print("export SC_AUTH_METHOD=oidc")
EOF
)"
ansible-playbook -i localhost, -i hypercore_inventory_ansible_both_false.yml run_ansible_both_false_tests.yml

ansible-playbook cleanup.yml
