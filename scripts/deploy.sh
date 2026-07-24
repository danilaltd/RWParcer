#!/bin/bash

set -euo pipefail

trap 'echo "FAILED at line $LINENO"' ERR

start_time=$(date +%s)

export REPO=$(echo "$GITHUB_REPOSITORY" | tr '[:upper:]' '[:lower:]')
export IMAGE_TAG="${ENVIRONMENT}-${GITHUB_SHA}"
export DATA_DIR="/var/lib/rwparcer-${ENVIRONMENT}/data"
export PROXY_DB_PATH="/var/lib/rwparcer-${ENVIRONMENT}/proxies.db"

echo "Starting deployment for ${ENVIRONMENT} environment"
echo "Repository: ${REPO}"
echo "Image tag: ${IMAGE_TAG}"

docker login ghcr.io \
    -u "$GITHUB_ACTOR" \
    -p "$GITHUB_TOKEN"

mkdir -p "$DATA_DIR"

export PARSER_IMAGE="ghcr.io/$REPO-parser:$IMAGE_TAG"
export PROXY_MANAGER_IMAGE="ghcr.io/$REPO-proxy-manager:$IMAGE_TAG"

export COMPOSE_PROJECT_NAME="rwparcer-$ENVIRONMENT"

echo "Pulling images..."
docker compose pull --parallel

echo "Starting new containers..."
docker compose up -d --remove-orphans

echo "Waiting for services to be healthy..."
timeout 300 bash -c 'until docker compose ps --format json | grep -q proxy-manager.*healthy; do echo "Waiting for service..."; sleep 5; done'

end_time=$(date +%s)
echo "Deployment took $((end_time - start_time)) seconds"
echo "Deployment successful!"