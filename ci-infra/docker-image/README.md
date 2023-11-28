This build docker iamge for running some of CI jobs.
We need to build new iamge when:
 - we want to test with new ansible-core

To build a new image:

```
# Bump ANSIBLE_CORE_VERSION
nano Dockerfile

# Bump DOCKER_IMAGE_TAG
# Use something like 9-dev0 for testing, then switch to 9 when image works.
nano build.sh

./build.sh
# new image is pushed to quay.io
```

Minimal local test of the new image:

```
# git code is at path .../ansible_collections/scale_computing/hypercore
docker run --rm -it -w /code/ansible_collections/scale_computing/hypercore -v $PWD/../../..:/code quay.io/justinc1_github/scale_ci_integ:9-dev0 bash
git config --global --add safe.directory $PWD
ansible-test units --local --python 3.10
ansible-test sanity --local --python 3.10
```
