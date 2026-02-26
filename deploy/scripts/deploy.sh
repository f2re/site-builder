#!/bin/bash
# Deployment Helper Script
# This script is executed on the production server via SSH.

set -e

PROJECT_ROOT="/srv/site-builder"
IMAGE_TAG=$1

if [ -z "$IMAGE_TAG" ]; then
    echo "Usage: $0 <IMAGE_TAG>"
    exit 1
fi

cd $PROJECT_ROOT

echo "--- Deployment started with tag: $IMAGE_TAG ---"

# Export IMAGE_TAG for docker-compose.prod.yml
export IMAGE_TAG=$IMAGE_TAG

echo "--- Pulling new images ---"
docker compose -f deploy/docker-compose.prod.yml pull

echo "--- Restarting services ---"
docker compose -f deploy/docker-compose.prod.yml up -d --remove-orphans

echo "--- Pruning old images ---"
docker image prune -f

echo "--- Deployment finished successfully! ---"
