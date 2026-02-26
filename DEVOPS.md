# GitLab CI/CD & Deployment Guide

This guide describes how to deploy the **site-builder** system using GitLab CI/CD with automatic deployment on version tags.

## 1. Server Preparation

Run the setup script on your production server to install Docker and create the necessary directory structure:

```bash
# On the production server
chmod +x deploy/scripts/setup_server.sh
./deploy/scripts/setup_server.sh
```

## 2. GitLab Runner Setup

Deploy a GitLab Runner (agent) to execute your CI/CD pipelines. You can run it on the same server or a separate one.

1.  Go to your GitLab project -> **Settings** -> **CI/CD** -> **Runners**.
2.  Click **New project runner**.
3.  Copy the **Registration Token**.
4.  Run the setup script:

```bash
chmod +x deploy/scripts/setup_runner.sh
./deploy/scripts/setup_runner.sh <YOUR_REGISTRATION_TOKEN>
```

## 3. GitLab CI/CD Variables

Configure the following variables in **Settings** -> **CI/CD** -> **Variables**:

| Variable | Type | Description |
|---|---|---|
| `SSH_PRIVATE_KEY` | File | Private SSH key to access the production server. |
| `PROD_HOST` | Variable | IP address or domain of the production server. |
| `DEPLOY_USER` | Variable | SSH user for deployment (e.g., `root` or `deploy`). |
| `STAGING_HOST` | Variable | IP address or domain of the staging server. |

## 4. Deployment Workflow

### Branch Deployment (Manual)
When you push to the `main` branch, the pipeline will build the images and wait for a **manual trigger** in the `deploy_prod` stage.

### Tag Deployment (Automatic)
When you push a version tag (e.g., `v1.0.0`), the system will:
1.  Build Docker images with the version tag (`:v1.0.0`).
2.  Push them to the GitLab Container Registry.
3.  **Automatically deploy** them to the production server.

**How to push a tag:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 5. Directory Structure on Server

The deployment happens in `/srv/site-builder`.
- `.env.prod`: Must be created manually on the server.
- `data/`: Contains persistent volumes for Postgres, Redis, etc.
- `deploy/`: Contains deployment configurations.

## 6. Verification

After deployment, check the status:
```bash
docker compose -f deploy/docker-compose.prod.yml ps
```
And view logs:
```bash
docker compose -f deploy/docker-compose.prod.yml logs -f
```
