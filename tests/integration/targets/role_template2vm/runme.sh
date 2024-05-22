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
print("export SC_VIRTUAL_DISK_IS_SUPPORTED='{}'".format(data["sc_config"][sc_host]["features"]["virtual_disk"]["is_supported"]))
print("export SC_VERSION_UPDATE_CURRENT_VERSION='{}'".format(data["sc_config"][sc_host]["features"]["version_update"]["current_version"]))
EOF
)"

env | grep SC_

if [ "$SC_VIRTUAL_DISK_IS_SUPPORTED" != "True" ]
then
  echo "Virtual disk feature is not supported, not testing template2vm" 2>&1
  exit 0
fi
if (echo "$SC_VERSION_UPDATE_CURRENT_VERSION" | grep "^9\.2\.")
then
  echo "Virtual disk feature on HyperCore 9.2 is experimental, not testing template2vm" 2>&1
  exit 0
fi

set -eux

# Inject hypercore_inventory.yml with needed values before running tests
# Use examples/hypercore_inventory.yml as template.
# cat file to fail early if hypercore_inventory.yml is missing.
cat "$(dirname "$(realpath "$0")")/hypercore_inventory.yml"

# This is needed for scale_computing.hypercore.template2vm role, tasks wait_vm_boot_tasks.yml
# Otherwise local venv python interpreter was "not found" on target VM.
export ANSIBLE_PYTHON_INTERPRETER=/usr/bin/python3

function cleanup {
    unset ANSIBLE_CACHE_PLUGIN
    unset ANSIBLE_CACHE_PLUGIN_CONNECTION
}

trap 'cleanup "$@"' EXIT


ansible-playbook -e @vars.yml cleanup.yml
ansible-playbook -e @vars.yml prepare.yml

ansible-playbook -i hypercore_inventory.yml -e @vars.yml 01_minimal.yml -vv
ansible-playbook -i hypercore_inventory.yml -e @vars.yml -e @02_vars.yml 02_booted.yml -vv
ansible-playbook -i hypercore_inventory.yml -e @vars.yml 03_extra_nics.yml -vv

ansible-playbook -e @vars.yml cleanup.yml
