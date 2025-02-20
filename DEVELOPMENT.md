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

# For convience you can store the environ variables into .sh or .env file in git-ignored directory:
cat <EOF >>ci-infra/local-dev/env-host-4.sh
export SC_HOST=https://1.2.3.4
export SC_USERNAME=admin
export SC_PASSWORD=admin_pass
EOF
source ci-infra/local-dev/env-host-4.sh
```

## Debugging

Requests sent to and responses received from HyperCore can be written to a file for debugging.
Environ variable `SC_DEBUG_LOG_TRAFFIC=1` should be set, and `q` python library needs to be installed.
The output is written to file `/tmp/q` on Ansible controller.

Note that `/tmp/q` will contain login passwords, HTTP session cookies and other sensitive data.
It should not be shared around.

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

## Required CI services/infrastructure

Some tests need additional infrastructure
- SMB server for testing VM import/export
- NTP server for testing NTP configuration
- OIDC client and test username/password to test OIDC login.

### CI SMB server

Existing SMB server is reused.
It was setup by ScaleComnputing for demo purposes (for potentional customers).

Details:

- IP 10.5.11.39 (see `tests/integration/integration_config.yml.j2`)
- CI tests should use only `/cidata` and subdirectories

### CI NTP server

NTP server is running on VM with github runner.
It is a regular systemd service - `systemctl status chrony`.

Details:

- IP 10.5.11.5

### CI OIDC client

ScaleComnputing (Dave) created a test user in Azure.
See `tests/integration/integration_config.yml.j2` and GitHub CI vars/secrets.

Details:

- We need to periodically reset password, it expires (every 3 months or something).
  Visit https://login.microsoftonline.com/, login as xlabciuser@scalemsdnscalecomputing.onmicrosoft.com.
  After password change:
  - every developer need to update local integration_config.yml
  - update github secret `OIDC_USERS_0_PASSWORD`

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

# Adding new CI test cluster

The CI test clusters are VSNSs - virtual single node clusters.
ScaleComputing does setup new VSNS, with suitable HyperCore version installed.

Steps:
 - Request / reserve static IP address from Alex
   - either replacing existing static IP or using next in series 105.11.20x
 - create empty VM with 1 virtio disk, type other, tag hc3nested, 16GB ram, 4 cores.
 - image new vSNS node using test iso image (vs. release - this may change in upcoming releases)
 - (optional) Save it as template VM, example name `vsns9213-unconfigured`
 - as admin/admin
   - run `sudo scnodeinit` to configure IPs,
   - `sudo singleNodeCluster=1 scclusterinit`
 - Save it as template VM, example name `vsns9213-template`
 - Create a final vSNS from template VM, example name `vsns9213-ci`
 - Add vSNS login URL to Azure OIDC redirectUris
   - ensure ip address is added to entraAD (azure) app registration for OIDC integration (ask Dave if needed)
      - "app_display_name": "Scale Computing HC3",
      - "app_id": "d2298ec0-0596-49d2-9554-840a2fe20603",

## Reset VSNS test cluster

After enough testing VSNS test clusters get slow.
CI integration testing takes say 8 hours instead of 1 hour.
At that time we recreate VSNS from template VM.
Run:

```bash
ansible-playbook ci-infra/helpers/ci_hosts_recreate.yml -v
```
