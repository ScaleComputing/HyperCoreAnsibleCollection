# cluster_config

Role version_update_single_node can be used to:
- update version on Scale Computing HyperCore cluster ([main.yml](tasks/main.yml)).
- shutdown all running VMs or only a running VMs with specific tag/tags ([shutdown_vms.yml](tasks/shutdown_vms.yml) ).
- start previously running VMs ([restart_vms.yml](tasks/restart_vms.yml)).

## Requirements

- Role can be used on a single node cluster only.

## Role Variables

See [argument_specs.yml](../../roles/version_update_single_node/meta/argument_specs.yml).

## Limitations

- NA

## Dependencies

- NA

## Example Playbook

See [version_update_single_node.yml](../../examples/version_update_single_node.yml).

## License

GNU General Public License v3.0 or later

See [LICENSE](../../LICENSE) to see the full text.
