# Usage: build new image locally, push it to gcr, use it in CI. and

# we use 'pip install name~=1.2.0' to install latest 1.2.x release
ARG ANSIBLE_CORE_VERSION=2.17.0

# =======================================================================
FROM python:3.12-slim-bookworm
ARG ANSIBLE_CORE_VERSION

ENV LANG=en_US.UTF-8

RUN apt update && apt install -y git make smbclient genisoimage qemu-utils jq sudo procps locales rsync
RUN sed -i '/en_US.UTF-8/s/^# //' /etc/locale.gen && locale-gen
RUN pip install --upgrade pip wheel

COPY all.requirements /code/ci-infra/docker-image/
RUN pip install -r /code/ci-infra/docker-image/all.requirements && \
    pip install yq jinja2-cli

RUN pip install ansible-core~=$ANSIBLE_CORE_VERSION
