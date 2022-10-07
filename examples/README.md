# About

The `(examples` subdirectory contains usage examples for individual modules.
A copy-paste ansible commands are listed below.

# Preparation

You need to install ansible, the `scale_computing.hypercore` collection,
and export required environment variables (`SC_HOST` etc.) to define target HyperCore cluster.
Details are in [DEVELOPMENT.md](../DEVELOPMENT.md), section "Prepare development environment".

# Examples

The examples are run from localhost (`ansible-playbook -i localhost,` part),
and playbooks contain `connection: local`.
This allows to use environ variables from local shell environment.

If ansible executes an example via SSH connection (e.g. without `connection: local`),
then you need to add to example environment section with `SC_HOST` and other environment variables.
For example please see file [iso_info.yml](iso_info.yml).

## Modules iso, iso_info

```shell script
# List ISO images
ansible-playbook -i localhost, examples/iso_info.yml

# Get TinyCore-current.iso from http://tinycorelinux.net/
ansible-playbook -i localhost, examples/iso.yml

# Remove old TinyCore-current.iso if present, to force re-upload
ansible-playbook -i localhost, -e iso_remove_old_image=True examples/iso.yml
```

## Module vm__info

```shell
# Show info about specific VM
ansible-playbook -i localhost, -e vm_name=demo-vm examples/vm_info.yml
```

## Module vm_replication_info

```shell
# Show info about specific VM replication settings
ansible-playbook -i localhost, -e vm_name=demo-vm examples/vm_replication_info.yml
```

## Module api

```shell script
# Get cluster info
ansible-playbook -i localhost, examples/api_get_cluster_info.yml
```
