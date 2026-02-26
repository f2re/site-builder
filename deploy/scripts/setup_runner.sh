#!/bin/bash
# GitLab Runner Setup Script
# Supports GitLab 16+ new runner authentication token format (glrt-...).
# Configuration (tags, locked, run-untagged) is managed on the GitLab server side.

set -e

# --- Configuration ---
RUNNER_NAME=${RUNNER_NAME:-"site-builder-runner"}
GITLAB_URL=${GITLAB_URL:-"https://gitlab.wifiobd.ru/"}
# Authentication token (glrt-...) provided as first argument
AUTH_TOKEN=$1

if [ -z "$AUTH_TOKEN" ]; then
    echo "Usage: $0 <AUTH_TOKEN>"
    echo "Get your token in GitLab -> Settings -> CI/CD -> Runners -> New project runner"
    exit 1
fi

echo "--- Installing Docker if missing ---"
if ! [ -x "$(command -v docker)" ]; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker installed. You may need to re-login for group changes to take effect."
fi

# Remove existing runner container if present
if docker ps -a --format '{{.Names}}' | grep -q "^${RUNNER_NAME}$"; then
    echo "--- Removing existing runner container ---"
    docker rm -f "$RUNNER_NAME"
fi

echo "--- Deploying GitLab Runner Container ---"
docker run -d \
    --name "$RUNNER_NAME" \
    --restart always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v gitlab-runner-config:/etc/gitlab-runner \
    gitlab/gitlab-runner:latest

echo "--- Registering Runner ---"
docker exec "$RUNNER_NAME" gitlab-runner register \
    --non-interactive \
    --url "$GITLAB_URL" \
    --token "$AUTH_TOKEN" \
    --executor "docker" \
    --docker-image "docker:24" \
    --description "$RUNNER_NAME" \
    --docker-volumes "/var/run/docker.sock:/var/run/docker.sock"

echo "--- Runner $RUNNER_NAME is ready! ---"
echo "Check status at: ${GITLAB_URL}admin/runners"
