from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
)

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
# In production, Nginx should serve this directory
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name="media")


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
