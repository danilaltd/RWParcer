#!/bin/bash

set -e

export REPO=$(echo "$GITHUB_REPOSITORY" | tr '[:upper:]' '[:lower:]')
export IMAGE_TAG="${ENVIRONMENT}-${GITHUB_SHA}"
export DATA_DIR="/var/lib/rwparcer-${ENVIRONMENT}/data"
export PROXY_DB_PATH="/var/lib/rwparcer-${ENVIRONMENT}/proxies.db"

docker login ghcr.io \
    -u "$GITHUB_ACTOR" \
    -p "$GITHUB_TOKEN"

mkdir -p "$DATA_DIR"

export PARSER_IMAGE="ghcr.io/$REPO-parser:$IMAGE_TAG"
export PROXY_MANAGER_IMAGE="ghcr.io/$REPO-proxy-manager:$IMAGE_TAG"

export COMPOSE_PROJECT_NAME="rwparcer-$ENVIRONMENT"

docker compose pull

docker compose up -d --remove-orphans