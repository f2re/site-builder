# Module: tests/unit/test_blog_pagination.py | Agent: backend-agent | Task: p28_backend_blog_categories
"""Unit tests for blog pagination cursor encoding/decoding."""
import base64
import json
import uuid
from datetime import datetime, timezone

import pytest

from app.api.v1.blog.repository import _encode_cursor, _decode_cursor


def test_encode_cursor_with_published_at() -> None:
    """Cursor encodes published_at and id correctly."""
    post_id = uuid.uuid4()
    published_at = datetime(2026, 3, 8, 12, 0, 0, tzinfo=timezone.utc)
    cursor = _encode_cursor(published_at, post_id)
    assert isinstance(cursor, str)
    # Must be valid base64
    decoded_bytes = base64.urlsafe_b64decode(cursor.encode())
    payload = json.loads(decoded_bytes.decode())
    assert payload["id"] == str(post_id)
    assert payload["published_at"] == published_at.isoformat()


def test_encode_cursor_without_published_at() -> None:
    """Cursor with None published_at stores empty string."""
    post_id = uuid.uuid4()
    cursor = _encode_cursor(None, post_id)
    payload = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
    assert payload["published_at"] == ""
    assert payload["id"] == str(post_id)


def test_decode_cursor_roundtrip() -> None:
    """Encode then decode returns the same values."""
    post_id = uuid.uuid4()
    published_at = datetime(2026, 1, 15, 9, 30, 0, tzinfo=timezone.utc)
    cursor = _encode_cursor(published_at, post_id)
    result = _decode_cursor(cursor)
    assert result is not None
    decoded_published_at, decoded_id = result
    assert decoded_id == post_id
    assert decoded_published_at == published_at


def test_decode_cursor_invalid_returns_none() -> None:
    """Invalid cursor returns None instead of raising."""
    assert _decode_cursor("not_valid_base64!!!") is None
    assert _decode_cursor("") is None
    assert _decode_cursor("e30=") is None  # {} — missing 'id' key


def test_decode_cursor_missing_id_returns_none() -> None:
    """Cursor missing 'id' field returns None."""
    payload = json.dumps({"published_at": "2026-01-01T00:00:00+00:00"})
    bad_cursor = base64.urlsafe_b64encode(payload.encode()).decode()
    assert _decode_cursor(bad_cursor) is None


def test_decode_cursor_empty_published_at() -> None:
    """Cursor with empty published_at returns None for datetime."""
    post_id = uuid.uuid4()
    cursor = _encode_cursor(None, post_id)
    result = _decode_cursor(cursor)
    assert result is not None
    decoded_published_at, decoded_id = result
    assert decoded_published_at is None
    assert decoded_id == post_id
