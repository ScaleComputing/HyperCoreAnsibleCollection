# cluster_config

Role cluster_config can be used to:
- fully configure a new HyperCore server
- partially reconfigure an existing HyperCore server

The role will continue with cluster configuration tasks if one of tasks fail,
to apply as many changes as possible.
Whole role will still exit with error.

## Requirements

- NA

## Role Variables

See [argument_specs.yml](../../roles/cluster_config/meta/argument_specs.yml).

## Limitations

- NA

## Dependencies

- NA

## Example Playbook

See [cluster_config.yml](../../examples/cluster_config.yml).

## License

GNU General Public License v3.0 or later

See [LICENSE](../../LICENSE) to see the full text.
