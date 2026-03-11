from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import os
import structlog
from pathlib import Path

from app.api.v1.router import api_router
from app.core.config import settings

logger = structlog.get_logger()

MEDIA_FALLBACK_ROOT = Path(os.getenv("MEDIA_FALLBACK_ROOT", "/tmp/site-builder-media"))


def get_cors_origins() -> list[str]:
    origins = list(settings.BACKEND_CORS_ORIGINS or [])
    dev_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    result: list[str] = []
    for origin in [*origins, *dev_origins]:
        if origin and origin not in result:
            result.append(origin)

    return result


def resolve_media_root() -> str:
    configured_root = Path(settings.MEDIA_ROOT)
    candidates = [configured_root, MEDIA_FALLBACK_ROOT]
    last_error = None

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            if candidate != configured_root:
                logger.warning(
                    "media_root_fallback_enabled",
                    configured_root=str(configured_root),
                    fallback_root=str(candidate),
                )
            return str(candidate)
        except OSError as exc:
            last_error = exc

    raise RuntimeError(f"Unable to initialize writable media root: {last_error}")


RESOLVED_MEDIA_ROOT = resolve_media_root()


app = FastAPI(
    title="WifiOBD Shop API",
    version="1.0.8",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    redirect_slashes=False,
)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

try:
    app.mount(settings.MEDIA_URL, StaticFiles(directory=RESOLVED_MEDIA_ROOT), name="media")
except OSError as e:
    logger.warning("media_dir_unavailable", path=RESOLVED_MEDIA_ROOT, error=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.8"}


@app.on_event("startup")
async def startup():
    logger.info(
        "api_startup",
        version="1.0.8",
        cors_origins=get_cors_origins(),
        media_root=RESOLVED_MEDIA_ROOT,
    )


@app.on_event("shutdown")
async def shutdown():
    logger.info("api_shutdown")
