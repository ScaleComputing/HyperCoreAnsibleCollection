#!/usr/bin/env bash

# Usage:
# docker login quay.io, with robot account (justinc1_github+justin_scale_uploader )
# ./build.sh
#
# For quicker testing, run "DOCKER_CACHE='y' ./build.sh"

set -eux

# Where to push images
DOCKER_REGISTRY_REPO=quay.io/justinc1_github/scale_ci_integ
# Tag to push
DOCKER_IMAGE_TAG=10

DOCKER_CACHE="${DOCKER_CACHE:-n}"
if [ "$DOCKER_CACHE" == "n" ]
then
    DOCKER_BUILD_OPT="--no-cache"
else
    DOCKER_BUILD_OPT=""
fi

THIS_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
REPO_DIR="$(realpath "$THIS_SCRIPT_DIR/../.." )"

cat "$REPO_DIR"/{docs,test,sanity,mypy}.requirements > all.requirements
# TODO but is ghrc.io feature available/enabled?
# Or push to quay.io?
docker build $DOCKER_BUILD_OPT -t "$DOCKER_REGISTRY_REPO:$DOCKER_IMAGE_TAG" .
if [ "$DOCKER_CACHE" == "n" ]
then
    # Upload only cleanly build images
    # Do not overwrite existing tags.
    docker manifest inspect $DOCKER_REGISTRY_REPO:$DOCKER_IMAGE_TAG 1>/dev/null && \
        echo Image tag $DOCKER_REGISTRY_REPO:$DOCKER_IMAGE_TAG already pushed to registry 1>&2 && \
        exit 1
    docker push $DOCKER_REGISTRY_REPO:$DOCKER_IMAGE_TAG
fi
