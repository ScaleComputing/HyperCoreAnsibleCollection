---
name: Bug report
about: Create a report to help us improve

---

<!-- Summary. -->

## Expected Result

<!-- What you expected. -->

## Actual Result

<!-- What happened instead. -->

## Reproduction Steps

Please include a minimal playbook and other files needed to reproduce bug.
Provide either a link to files/repository (preferred option), or verbatim content.

```shell
ansible-playbook -i localhost -e @vars.yml my_playbook.yml -v
<paste output here>

cat my_playbook.yml
<paste output here>
# other relevant files - ansible.cfg, inventory.yml, vars.yml, etc.
```

## System Information

    $ ansible --version
    $ ansible-galaxy collection list

```
# paste output here
```

Please tell us also HyperCore version.

```
# HyperCore version here
```
