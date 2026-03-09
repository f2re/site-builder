@orchestrator fix building, run tests and lint and commit:
ading artifacts from coordinator... ok        correlation_id=01KK8KHEATVJ1V0ZJEJB46RFAT host=gitlab.wifiobd.ru id=1440 responseStatus=200 OK token=64_8-8KAM
Executing "step_script" stage of the job script 00:16
Using effective pull policy of [always] for container docker:24
Using docker image sha256:e31dbb0fb5be21256b536b8650b8a7dc3dcf2f72167c8d486685e272df439e7a for docker:24 with digest docker@sha256:9b17a9f25adf17b88d0a013b4f00160754adf4b07ccbe9986664a49886c2c98e ...
$ docker login -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN $CI_REGISTRY
WARNING! Using --password via the CLI is insecure. Use --password-stdin.
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store
Login Succeeded
$ docker pull $IMAGE_FRONTEND:latest || true
latest: Pulling from f2re/wifiobd2-site-modern/frontend
Digest: sha256:1aa26c3b795de1d476cc95a0d22cb4a04eef9e0c52af11a5592467ee30411f56
Status: Image is up to date for registry.gitlab.wifiobd.ru/f2re/wifiobd2-site-modern/frontend:latest
registry.gitlab.wifiobd.ru/f2re/wifiobd2-site-modern/frontend:latest
$ docker build --cache-from $IMAGE_FRONTEND:latest -t $IMAGE_FRONTEND:$DYNAMIC_TAG -t $IMAGE_FRONTEND:latest ./frontend
#0 building with "default" instance using docker driver
#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 1.66kB done
#1 DONE 0.0s
#2 [internal] load metadata for docker.io/library/node:22-slim
#2 DONE 0.8s
#3 [internal] load .dockerignore
#3 transferring context: 352B done
#3 DONE 0.0s
#4 importing cache manifest from registry.gitlab.wifiobd.ru/f2re/wifiobd2-site-modern/frontend:latest
#4 DONE 0.0s
#5 [builder 1/8] FROM docker.io/library/node:22-slim@sha256:9c2c405e3ff9b9afb2873232d24bb06367d649aa3e6259cbe314da59578e81e9
#5 DONE 0.0s
#6 [internal] load build context
#6 transferring context: 2.82MB 0.1s done
#6 DONE 0.1s
#7 [builder 4/8] RUN npm install -g npm@latest
#7 CACHED
#8 [builder 3/8] RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl python3 make g++     && rm -rf /var/lib/apt/lists/*
#8 CACHED
#9 [builder 5/8] COPY package*.json ./
#9 CACHED
#10 [builder 2/8] WORKDIR /app
#10 CACHED
#11 [builder 6/8] RUN npm install
#11 CACHED
#12 [builder 7/8] COPY . .
#12 DONE 0.0s
#13 [builder 8/8] RUN npm run build
#13 0.694
#13 0.694 > build
#13 0.694 > nuxt build
#13 0.694
#13 1.248 ┌  Building Nuxt for production...
#13 1.566 │
#13 1.566 ●  Nuxt 4.3.1 (with Nitro 2.13.1, Vite 7.3.1 and Vue 3.5.29)
#13 3.875 ✔ Nuxt Icon discovered local-installed 3 collections: logos, ph, simple-icons
#13 4.144 │
#13 4.144 ●  Nitro preset: node-server
#13 5.553 ℹ Building client...
#13 5.571 ℹ vite v7.3.1 building client environment for production...
#13 5.654 ℹ transforming...
#13 13.86 ℹ ✓ 578 modules transformed.
#13 13.87
#13 13.87  ERROR  ✗ Build failed in 8.30s
#13 13.87
#13 13.87 │
#13 13.87 ■  Nuxt build error: Error: [vite:load-fallback] Could not load /app//components/admin/ProductOptionGroupsEditor.vue (imported by pages/admin/products/[id].vue?vue&type=script&setup=true&lang.ts): ENOENT: no such file or directory, open '/app//components/admin/ProductOptionGroupsEditor.vue'
#13 ERROR: process "/bin/sh -c npm run build" did not complete successfully: exit code: 1
------
 > [builder 8/8] RUN npm run build:
4.144 ●  Nitro preset: node-server
5.553 ℹ Building client...
5.571 ℹ vite v7.3.1 building client environment for production...
5.654 ℹ transforming...
13.86 ℹ ✓ 578 modules transformed.
13.87
13.87  ERROR  ✗ Build failed in 8.30s
13.87
13.87 │
13.87 ■  Nuxt build error: Error: [vite:load-fallback] Could not load /app//components/admin/ProductOptionGroupsEditor.vue (imported by pages/admin/products/[id].vue?vue&type=script&setup=true&lang.ts): ENOENT: no such file or directory, open '/app//components/admin/ProductOptionGroupsEditor.vue'
------
Dockerfile:48
--------------------
  46 |     ARG NUXT_PUBLIC_API_BASE=http://backend:8000/api/v1
  47 |     ENV NUXT_PUBLIC_API_BASE=$NUXT_PUBLIC_API_BASE
  48 | >>> RUN npm run build
  49 |
  50 |
--------------------
ERROR: failed to solve: process "/bin/sh -c npm run build" did not complete successfully: exit code: 1
Cleaning up project directory and file based variables 00:01
ERROR: Job failed: exit code 1