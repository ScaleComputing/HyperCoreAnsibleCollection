# Prepare development environment

Create python venv and clone code.

```
mkdir -p ansible_collections/scale_computing/
cd ansible_collections/scale_computing/

python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# ansible-core==2.13.1 was used during development and testing,
# but version from 2.9.x up should work
pip install ansible-core

git clone git@github.com:ScaleComputing/HyperCoreAnsibleCollection.git hypercore
cd hypercore

# Install community.general collection, since we like to have stdout_callback=community.general.yaml in ansible.cfg
ansible-galaxy collection install community.general community.crypto
# Optional, if you want to run "ansible-test --venv ..."
# pip install -r test.requirements -r sanity.requirements
```

The collection needs to know how to assess the destination HyperCore cluster.
Normally this is to playbooks via environ variables.
To be able to run example playbooks execute in shell:

```bash
export SC_HOST=https://1.2.3.4
export SC_USERNAME=admin
export SC_PASSWORD=admin_pass
```

# Integration tests configuration

For integration tests we need to configure access to test cluster.
Copy template and edit it:

```shell script
cp tests/integration/integration_config.yml.j2 tests/integration/integration_config.yml
nano tests/integration/integration_config.yml

# Partial sample content
cat tests/integration/integration_config.yml
sc_config:
  base_cfg: &base_cfg
    time_server:
      source: pool.ntp.org
    time_zone:
      zone: US/Eastern
      ...
  https://1.2.3.4:
    <<: *base_cfg
    sc_username: admin
    sc_password: admin_pass
    ...
```

## CI jobs for integration tests

Github CI jobs require some infrastructure:
- Dedicated github runner(s), with access to test HyperCore cluster(s).
  - We test against multiple HyperCore versions (9.1, 9.2 etc.).
- Test HyperCore clusters
  - Currently, a single physical HyperCore cluster is used (https://10.5.11.50).
  - It runs two VSNS VMs (virtual single node systems) - for versions 9.1 (https://10.5.11.200) and 9.2 (https://10.5.11.201).
  - Each VSNS VM was prepared manually (how - ask Dave), VM was shutdown and we use it as base VM image.
    Base VM was cloned to obtain final VSNS VM.
- A docker image for CI jobs, with needed tools preinstalled (ansible-core, jq, and other utilities).
  - File [build.sh](ci-infra/docker-image/build.sh) is used to build and push docker image.
  - Docker image is built manually, on local workstation.
  - Only authenticated users can publish new image - docker-login is required before `docker push`.
  - Anyone can download built image. Do not include sensitive data into the image.
- Configured github secrets.
  - In many cases, password is stored in github secrets, but corresponding username is not

Some tests need additional infrastructure
- SMB server for testing VM import/export
- NTP server for testing NTP configuration
- OIDC client and test username/password to test OIDC login.

# Development

Included `Makefile` contains shortcuts for common development tasks,
running tests, linter, code formatting, source directory cleanup etc.
To list all available commands, run just `make`, and you will get something like:

```
(.venv) [me@mypc hypercore]$ make
Available targets:
clean:  ## Remove all auto-generated files
format:  ## Format python code with black
integration:  ## Run integration tests
sanity:  ## Run sanity tests
units:  ## Run unit tests
```

If you want to run tests with a single python version (e.g. not with whole test matrix), use:

```
ansible-test sanity --venv
ansible-test units --venv
ansible-test integration --venv
```

Build collection.

```yaml
antsibull-changelog release
ansible-galaxy collection build
```

Run sample playbook.
Sample ansible.cfg is there to ensure collection does not need to be installed.

```yaml
ansible-playbook -i localhost, examples/iso_info.yml -v
```

## Creating a release

Releases are automatically created when a tag is created with a name matching
`v*.*.*`. Before tagging a commit, create a release issue and complete all of
the prerequisites.

- Create a new release issue with the "[New
  release](https://github.com/ScaleComputing/HyperCoreAnsibleCollection/issues/new/choose)."
  template
- Complete each of the items in the release steps checklist
