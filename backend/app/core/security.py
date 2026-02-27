# Module: core/security.py | Agent: backend-agent | Task: phase7_backend_security
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(settings.FERNET_KEY.encode())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    role: str = "customer",
    expires_delta: timedelta | None = None,
) -> str:
    """Create JWT access token with user id, role and type claims."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "role": role,          # <-- role claim added
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def encrypt_data(plain_text: str) -> str:
    """Encrypt sensitive data using Fernet."""
    if not plain_text:
        return plain_text
    try:
        # Check if already encrypted
        fernet.decrypt(plain_text.encode())
        return plain_text
    except Exception:
        return fernet.encrypt(plain_text.encode()).decode()


def decrypt_data(encrypted_text: str) -> str:
    """Decrypt sensitive data using Fernet."""
    if not encrypted_text:
        return encrypted_text
    try:
        return fernet.decrypt(encrypted_text.encode()).decode()
    except (InvalidToken, Exception):
        # If it's not a valid Fernet token, it might be already plain text
        return encrypted_text


def get_blind_index(text: str) -> str:
    """Generate a blind index (hash) for searching encrypted fields."""
    if not text:
        return ""
    # Use SHA256 with a salt (SECRET_KEY) to prevent rainbow table attacks on the blind index
    # We lowercase the email for consistent searching
    return hashlib.sha256((text.lower() + settings.SECRET_KEY).encode()).hexdigest()
