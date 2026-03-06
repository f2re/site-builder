# Module: core/config.py | Agent: backend-agent | Task: phase11_backend_admin_blog_refinement
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices, field_validator
from typing import List, Union


class Settings(BaseSettings):
    # ── Project ───────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "WifiOBD Shop"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    NUXT_PUBLIC_SITE_URL: str = "http://localhost:3000"

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
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        validation_alias=AliasChoices("BACKEND_CORS_ORIGINS", "CORS_ORIGINS")
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str], None]) -> List[str]:
        if v is None:
            return ["http://localhost:3000", "http://localhost:5173"]
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, list):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@wifiobd.ru"
    EMAILS_FROM_NAME: str = "WifiOBD Shop"

    # ── Telegram ──────────────────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_NAME: str = "WifiOBD_Bot"
    TELEGRAM_CHAT_ID: str = ""  # Admin chat ID for notifications

    # ── OAuth ─────────────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    YANDEX_CLIENT_ID: str = ""
    YANDEX_CLIENT_SECRET: str = ""

    # ── External APIs ─────────────────────────────────────────────────────────
    YOOMONEY_SHOP_ID: str = ""
    YOOMONEY_SECRET: str = ""
    CDEK_CLIENT_ID: str = ""
    CDEK_CLIENT_SECRET: str = ""

    # ── OpenCart Migration ───────────────────────────────────────────────────
    OC_DB_HOST: str = "localhost"
    OC_DB_PORT: int = 3306
    OC_DB_NAME: str = ""
    OC_DB_USER: str = ""
    OC_DB_PASSWORD: str = ""
    OC_SITE_URL: str = ""
    OC_LANGUAGE_ID: int = 1

    # ── Media (Local Storage) ───────────────────────────────────────────────
    MEDIA_ROOT: str = "./media"  # Path inside Docker container
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
    MEILISEARCH_HOST: str = Field(
        default="http://meilisearch:7700",
        validation_alias=AliasChoices("MEILI_URL", "MEILISEARCH_URL", "MEILISEARCH_HOST")
    )
    MEILISEARCH_API_KEY: str = "masterKey"

    # ── Dashfirm Compiler ────────────────────────────────────────────────────
    COMPILER_PATH: str = "./compiler/compiler"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'
    )


settings = Settings()
