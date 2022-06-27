# Prepare development environment

Crete python venv and clone code.

```
python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install ansible-core  # 2.13.1

mkdir -p ansible_collections/scale_computing/
cd ansible_collections/scale_computing/
git clone ssh://git@gitlab.xlab.si:13022/scale-ansible-collection/scale-computing-hc3-ansible-collection.git hc3
cd hc3

# pip install -r test-requirements.txt -r sanity.requirements
```

Run tests, in venv or in container:

```
ansible-test sanity --venv
ansible-test units --venv
ansible-test integration --venv
```
