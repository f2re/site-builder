# Module: core/config.py | Agent: backend-agent | Task: phase11_backend_admin_blog_refinement
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    # ── Project ───────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "WifiOBD Shop"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FERNET_KEY: str = "duFJhEPYbl7bimupZ4q0-cDXqfiA62LIo1173T7iZpE="  # Generated for 152-FZ PII encryption

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/wifiobd"

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # ── CORS ──────────────────────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@wifiobd.ru"
    EMAILS_FROM_NAME: str = "WifiOBD Shop"

    # ── Telegram ──────────────────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""  # Admin chat ID for notifications

    # ── External APIs ─────────────────────────────────────────────────────────
    YOOMONEY_SHOP_ID: str = ""
    YOOMONEY_SECRET: str = ""
    CDEK_CLIENT_ID: str = ""
    CDEK_CLIENT_SECRET: str = ""

    # ── Media (Local Storage) ───────────────────────────────────────────────
    MEDIA_ROOT: str = "/app/media"  # Path inside Docker container
    MEDIA_URL: str = "/media"        # Public URL prefix
    
    # ── MinIO / S3 (DEPRECATED: Switching to Local Storage) ──────────────────
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET: str = "wifiobd-media"
    MINIO_BUCKET_MEDIA: str = "media"  # Bucket for blog/product images
    MINIO_PUBLIC_DOMAIN: str = "media.wifiobd.shop"  # Public CDN domain
    MINIO_USE_SSL: bool = True
    MINIO_DELETE_ORIGINAL: bool = False  # Delete original after WebP conversion

    # ── Meilisearch ───────────────────────────────────────────────────────────
    MEILISEARCH_HOST: str = "http://localhost:7700"
    MEILISEARCH_API_KEY: str = "masterKey"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)


settings = Settings()
