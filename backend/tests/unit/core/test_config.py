# Module: tests/unit/core/test_config.py
import pytest
import os
from unittest.mock import patch
from app.core.config import Settings


def test_cors_origins_json_parsing():
    """Тест парсинга CORS_ORIGINS как JSON-списка."""
    with patch.dict(os.environ, {"CORS_ORIGINS": '["http://a.com", "http://b.com"]'}):
        settings = Settings(_env_file=None)
        assert settings.BACKEND_CORS_ORIGINS == ["http://a.com", "http://b.com"]


def test_cors_origins_comma_separated_parsing():
    """Тест парсинга CORS_ORIGINS как строки через запятую (не JSON)."""
    with patch.dict(os.environ, {"CORS_ORIGINS": "http://a.com, http://b.com"}):
        settings = Settings(_env_file=None)
        assert settings.BACKEND_CORS_ORIGINS == ["http://a.com", "http://b.com"]


def test_cors_origins_single_url_parsing():
    """Тест парсинга CORS_ORIGINS как одной ссылки (не JSON)."""
    with patch.dict(os.environ, {"CORS_ORIGINS": "http://a.com"}):
        settings = Settings(_env_file=None)
        assert settings.BACKEND_CORS_ORIGINS == ["http://a.com"]


def test_cors_origins_empty_string_parsing():
    """Тест парсинга пустой строки CORS_ORIGINS (должен вернуться дефолт)."""
    with patch.dict(os.environ, {"CORS_ORIGINS": ""}):
        settings = Settings(_env_file=None)
        # Дефолтные значения из Settings
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
        assert "http://localhost:5173" in settings.BACKEND_CORS_ORIGINS
