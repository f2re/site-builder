#!/bin/bash
set -e

PROJECT_ROOT="/srv/site-builder"
ENV_FILE="$PROJECT_ROOT/.env.prod"
COMPOSE_FILE="$PROJECT_ROOT/deploy/docker-compose.prod.yml"

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
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE not found!"
    echo "Copy deploy/.env.prod.example to $ENV_FILE and fill in real values."
    exit 1
fi

cd "$PROJECT_ROOT"

echo "--- Logging into GitLab Registry ---"
echo "$DEPLOY_TOKEN_PASS" | docker login "$CI_REGISTRY" -u "$DEPLOY_TOKEN_USER" --password-stdin

echo "--- Deployment started with tag: $IMAGE_TAG ---"
export IMAGE_TAG=$IMAGE_TAG
export CI_REGISTRY_IMAGE=$CI_REGISTRY_IMAGE

# --env-file loads .env.prod for ${VAR} substitution inside docker-compose.prod.yml
# (env_file: directive only injects vars into containers, not into compose YAML itself)
DC="docker compose -f $COMPOSE_FILE --env-file $ENV_FILE"

echo "--- Pulling new images ---"
$DC pull

echo "--- Restarting services ---"
$DC up -d --remove-orphans

echo "--- Pruning old images ---"
docker image prune -f

echo "--- Deployment finished: $IMAGE_TAG ---"
