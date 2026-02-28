#!/bin/bash
set -e

PROJECT_ROOT="/srv/site-builder"
IMAGE_TAG=$1
CI_REGISTRY=$2
DEPLOY_TOKEN_USER=$3
DEPLOY_TOKEN_PASS=$4
CI_REGISTRY_IMAGE=$5

if [ -z "$IMAGE_TAG" ] || [ -z "$CI_REGISTRY_IMAGE" ]; then
    echo "Usage: $0 <IMAGE_TAG> <CI_REGISTRY> <TOKEN_USER> <TOKEN_PASS> <CI_REGISTRY_IMAGE>"
    exit 1
fi

# Ensure required directories exist
mkdir -p "$PROJECT_ROOT/data/postgres"
mkdir -p "$PROJECT_ROOT/data/redis"
mkdir -p "$PROJECT_ROOT/data/meilisearch"
mkdir -p "$PROJECT_ROOT/deploy"

# Guard: abort if .env.prod is missing
if [ ! -f "$PROJECT_ROOT/.env.prod" ]; then
    echo "ERROR: $PROJECT_ROOT/.env.prod not found!"
    echo "Create it manually on the server before running deployment."
    exit 1
fi

cd "$PROJECT_ROOT"

echo "--- Logging into GitLab Registry ---"
echo "$DEPLOY_TOKEN_PASS" | docker login "$CI_REGISTRY" -u "$DEPLOY_TOKEN_USER" --password-stdin

echo "--- Deployment started with tag: $IMAGE_TAG ---"
export IMAGE_TAG=$IMAGE_TAG
export CI_REGISTRY_IMAGE=$CI_REGISTRY_IMAGE

echo "--- Pulling new images ---"
docker compose -f deploy/docker-compose.prod.yml pull

echo "--- Restarting services ---"
docker compose -f deploy/docker-compose.prod.yml up -d --remove-orphans

echo "--- Pruning old images ---"
docker image prune -f

echo "--- Deployment finished: $IMAGE_TAG ---"
