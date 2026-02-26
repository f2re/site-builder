#!/bin/bash
# GitLab Runner Setup Script
# This script installs Docker (if not present) and deploys a GitLab Runner as a container.

set -e

# --- Configuration ---
RUNNER_NAME=${RUNNER_NAME:-"site-builder-runner"}
GITLAB_URL=${GITLAB_URL:-"https://gitlab.com/"}
# Registration Token should be provided as environment variable
REGISTRATION_TOKEN=$1

if [ -z "$REGISTRATION_TOKEN" ]; then
    echo "Usage: $0 <REGISTRATION_TOKEN>"
    echo "You can find the registration token in GitLab -> Settings -> CI/CD -> Runners"
    exit 1
fi

echo "--- Installing Docker if missing ---"
if ! [ -x "$(command -v docker)" ]; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

echo "--- Deploying GitLab Runner Container ---"
docker run -d --name "$RUNNER_NAME" --restart always 
    -v /var/run/docker.sock:/var/run/docker.sock 
    -v gitlab-runner-config:/etc/gitlab-runner 
    gitlab/gitlab-runner:latest

echo "--- Registering Runner ---"
docker exec "$RUNNER_NAME" gitlab-runner register 
    --non-interactive 
    --url "$GITLAB_URL" 
    --registration-token "$REGISTRATION_TOKEN" 
    --executor "docker" 
    --docker-image "docker:24" 
    --description "$RUNNER_NAME" 
    --tag-list "docker,site-builder" 
    --run-untagged="true" 
    --locked="false" 
    --access-level="not_protected" 
    --docker-volumes "/var/run/docker.sock:/var/run/docker.sock"

echo "--- Runner $RUNNER_NAME is ready! ---"
