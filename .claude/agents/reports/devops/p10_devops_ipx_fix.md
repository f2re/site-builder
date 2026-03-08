## Status: DONE

## Completed:
- Added `ARG NUXT_PUBLIC_API_BASE=http://backend:8000/api/v1` to the builder stage of `frontend/Dockerfile` immediately before `RUN npm run build` (line 46)
- Added `ENV NUXT_PUBLIC_API_BASE=$NUXT_PUBLIC_API_BASE` immediately after the ARG line (line 47)
- This ensures `nuxt.config.ts` evaluates `process.env.NUXT_PUBLIC_API_BASE` at build time, so the IPX image alias resolves to `http://backend:8000/media` instead of a no-op `/media → /media` mapping

## Artifacts:
- `frontend/Dockerfile` — builder stage updated (lines 46–47)

## Root Cause Fixed:
Nuxt Image IPX uses a `alias` mapping defined in `nuxt.config.ts` at build time.
Without `NUXT_PUBLIC_API_BASE` set during `docker build`, the alias evaluated to
`undefined` and the path rewrite `/media → /media` was a no-op, causing
`IPX_FILE_NOT_FOUND` errors for all product images (including files with Cyrillic filenames).
With this fix, the alias becomes `/media → http://backend:8000/media`, allowing IPX
to proxy-fetch images from the backend container over the internal Docker network.

## Contracts Verified:
- `frontend/Dockerfile` edit: confirmed correct by file read (lines 46–47 in place)
- hadolint: pending user confirmation (Bash not permitted in this session)
  - Run manually: `docker run --rm -i hadolint/hadolint < frontend/Dockerfile`

## Next:
- frontend-agent or testing-agent: verify product images load correctly in staging with `docker compose up --build`
- If hadolint reports issues, re-run fix cycle

## Blockers:
- none
