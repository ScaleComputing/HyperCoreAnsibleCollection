# Prepare development environment

Create python venv and clone code.

```
mkdir -p ansible_collections/scale_computing/
cd ansible_collections/scale_computing/

python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install ansible-core  # 2.13.1

git clone ssh://git@gitlab.xlab.si:13022/scale-ansible-collection/scale-computing-hc3-ansible-collection.git hypercore
cd hypercore

# Install community.general collection, since we like to have stdout_callback=community.general.yaml in ansible.cfg
ansible-galaxy collection install community.general
# Optional, if you want to run "ansible-test --venv ..."
# pip install -r test.requirements -r sanity.requirements
```

For integration tests we need to configure access to test cluster.
Copy template and edit it:


```shell script
cp tests/integration/integration_config.yml.template tests/integration/integration_config.yml
nano tests/integration/integration_config.yml

# sample content
cat tests/integration/integration_config.yml
sc_host: https://1.2.3.4
sc_username: admin
sc_password: admin_pass
```

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
ansible-galaxy collection build
```

Run sample playbook.
Sample ansible.cfg is there to ensure collection does not need to be installed.

```yaml
ansible-playbook -i localhost, sample-playbook.yml -v
```
