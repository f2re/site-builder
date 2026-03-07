#!/bin/bash
# Production Server Setup Script
# This script prepares a clean Linux server for the site-builder system.

set -e

PROJECT_ROOT="/srv/site-builder"

echo "--- Installing Basic Dependencies ---"
sudo apt-get update
sudo apt-get install -y curl git gnupg lsb-release

echo "--- Installing Docker & Docker Compose ---"
if ! [ -x "$(command -v docker)" ]; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

echo "--- Creating Project Directories ---"
sudo mkdir -p $PROJECT_ROOT/data/postgres
sudo mkdir -p $PROJECT_ROOT/data/redis
sudo mkdir -p $PROJECT_ROOT/data/meilisearch
sudo chown -R $USER:$USER $PROJECT_ROOT

echo "--- Setup Complete! ---"
echo "Next steps:"
echo "1. Put your .env.prod file in $PROJECT_ROOT/.env.prod"
echo "2. Copy deploy/docker-compose.prod.yml to $PROJECT_ROOT/docker-compose.yml"
echo "3. Run 'docker compose up -d'"
