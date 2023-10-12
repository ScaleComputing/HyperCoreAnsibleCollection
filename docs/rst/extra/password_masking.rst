.. scale_computing.hypercore.password_masking:

****************
Password Masking
****************

**TL;DR** Even for testing avoid short password.

Ansible tries to prevent showing plaintext password, access token and
similar secrets in console output. This can cause some confusion,
especially when very short password is used (typical during testing).

Related to ScaleComputing HyperCore Ansible collection the most commonly
used password is the one used to login to HyperCore cluster (the ``SC_PASSWORD`` environ variable).
If this password is short, you will likely notice corrupted console output.
Also registered variables might contain wrong values, as value of password
in unrelated text will be masked.

Example
=======

As demonstration run a playbook ``examples/masked_password.yml`` in verbose mode.
The playbook will creates two users.
First task creates a user with username ``myuser`` and password ``mypass``.
Nothing special happens, output looks like:

..  code-block:: shell

    ansible-playbook examples/masked_password.yml -v
    ...
    TASK [Add test user myuser] ***********************************************
    changed: [localhost] => changed=true
      record:
        full_name: ''
        roles: []
        session_limit: 0
        username: myuser
        uuid: 2bacae2a-99de-413c-bca6-d5b448c1e5af

Second task creates a user with username ``myuser_mypass_bla`` and password ``mypass``.
Output looks like below:

..  code-block:: shell

    TASK [Add test user myuser_mypass_bla] ************************************
    changed: [localhost] => changed=true
      record:
        full_name: ''
        roles: []
        session_limit: 0
        username: myuser_********_bla
        uuid: bf1295b0-a289-406c-9e45-84ed2d06ed96

All occurrences of the password in the output were replaced by ``********`` string.
In this simple example the value of ``username`` got corrupted.
Instead of expected ``myuser_mypass_bla`` it contains ``myuser_********_bla``.

To prevent this do not use short passwords, as the value can be part of other unrelated string.
