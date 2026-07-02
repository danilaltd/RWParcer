#!/bin/bash

set -e

REPO=$(echo "$GITHUB_REPOSITORY" | tr '[:upper:]' '[:lower:]')

docker login ghcr.io \
    -u "$GITHUB_ACTOR" \
    -p "$GITHUB_TOKEN"

mkdir -p "$DATA_DIR"

export PARSER_IMAGE="ghcr.io/$REPO-parser:$IMAGE_TAG"
export PROXY_MANAGER_IMAGE="ghcr.io/$REPO-proxy-manager:$IMAGE_TAG"

export COMPOSE_PROJECT_NAME="rwparcer"

docker compose pull

docker compose up -d --remove-orphans