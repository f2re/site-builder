# GitLab CI/CD & Deployment Guide

This guide describes how to deploy the **site-builder** system using GitLab CI/CD with automatic deployment on version tags.

---

## 🚀 Scenario: GitLab on Machine A, Site on Machine B

This is the standard production setup. **Machine A** hosts your GitLab instance and Registry. **Machine B** is your remote production server where the website runs.

### 1. Prepare Machine B (Production Server)

Run the preparation script on **Machine B** to install Docker and setup directories:

```bash
# Execute on Machine B
curl -O https://raw.githubusercontent.com/.../deploy/scripts/setup_server.sh # or copy manually
chmod +x setup_server.sh
./setup_server.sh
```

### 2. Configure SSH Access (A → B)

For GitLab (Machine A) to "talk" to the Site Server (Machine B), you need SSH keys:

1.  **On your local machine**, generate a deploy key:
    ```bash
    ssh-keygen -t ed25519 -f ./deploy_key -N ""
    ```
2.  **On Machine B**: Add the content of `deploy_key.pub` to `~/.ssh/authorized_keys`.
3.  **On GitLab (Machine A)**: 
    - Go to **Settings** -> **CI/CD** -> **Variables**.
    - Add `SSH_PRIVATE_KEY` (Type: **File**). Paste the content of the private `deploy_key`.
    - Add `PROD_HOST` (Type: **Variable**). Value: IP address of Machine B.
    - Add `DEPLOY_USER` (Type: **Variable**). Value: `root` (or your user on Machine B).

### 3. Register GitLab Runner (Agent)

The Runner is the "worker" that builds your Docker images. It is best to install it on **Machine A** (where GitLab is) to avoid loading Machine B with builds.

1.  On GitLab: **Settings** -> **CI/CD** -> **Runners** -> **New project runner**.
2.  Copy the **Registration Token**.
3.  On **Machine A**, run:
    ```bash
    chmod +x deploy/scripts/setup_runner.sh
    ./deploy/scripts/setup_runner.sh <YOUR_TOKEN>
    ```

### 4. Automatic Deployment on Tags

Now, every time you push a version tag, the system handles everything:

```bash
# 1. Update version
git tag v1.0.1

# 2. Push to Machine A
git push origin v1.0.1
```

**What happens next:**
1.  **Machine A (Runner)**: Builds backend and frontend Docker images.
2.  **Machine A (Registry)**: Stores images with the `:v1.0.1` tag.
3.  **Machine A (CI/CD)**: Connects via SSH to **Machine B**.
4.  **Machine B**: Downloads images from Machine A's registry and restarts the site.

---

## 🛠 Manual Configuration

### Environment Secrets
You MUST create `/srv/site-builder/.env.prod` on **Machine B** manually before the first deployment. Use `.env.example` as a template.

### Registry Authentication
Machine B needs permission to pull images from Machine A. The CI/CD pipeline handles `docker login` automatically during the deploy stage, but ensure Machine B can reach Machine A's registry port (usually 5050 or 443).

## 📊 Verification & Logs

Check status on **Machine B**:
```bash
cd /srv/site-builder
docker compose -f deploy/docker-compose.prod.yml ps
docker compose -f deploy/docker-compose.prod.yml logs -f backend
```
