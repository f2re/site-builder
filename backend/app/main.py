from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import os
import structlog

from app.api.v1.router import api_router
from app.core.config import settings

logger = structlog.get_logger()

app = FastAPI(
    title="WifiOBD Shop API",
    version="1.0.8",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    # Отключаем автоматический redirect /path → /path/
    # Без этого FastAPI генерирует 307 с http:// Location (Apache→backend — plain HTTP),
    # что браузер блокирует как Mixed Content на HTTPS-странице.
    redirect_slashes=False,
)

# Доверяем X-Forwarded-Proto от Apache reverse proxy.
# Без этого FastAPI видит scheme="http" (внутреннее соединение) и строит
# redirect Location с http://, игнорируя заголовок X-Forwarded-Proto: https.
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Serve media files in development
# In production, Apache should serve this directory via ProxyPass /media/
try:
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name="media")
except OSError as e:
    logger.warning("media_dir_unavailable", path=settings.MEDIA_ROOT, error=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.8"}


@app.on_event("startup")
async def startup():
    logger.info("api_startup", version="1.0.8")


@app.on_event("shutdown")
async def shutdown():
    logger.info("api_shutdown")
