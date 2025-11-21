"""Security helpers for PulseML authentication."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext

from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a raw password against its hash.
    
    Truncates to 72 characters to match hashing behavior.
    """
    password_truncated = plain_password[:72]
    return pwd_context.verify(password_truncated, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.
    
    Bcrypt has a 72-byte limit. We truncate to 72 characters to stay well under the limit.
    For security, validation at the API level is preferred (see UserCreate schema).
    """
    # Truncate to 72 characters (which will always be <= 72 bytes for ASCII,
    # and at most 72*4 bytes for UTF-8, but we validate at API level)
    password_truncated = password[:72]
    return pwd_context.hash(password_truncated)


def _create_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    """Create a JWT token with the provided expiry."""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_access_token(subject: str) -> str:
    """Create an access token for the provided subject."""

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token({"sub": subject, "type": "access"}, expires_delta)


def create_refresh_token(subject: str) -> str:
    """Create a refresh token for the provided subject."""

    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token({"sub": subject, "type": "refresh"}, expires_delta)

