"""Authentication service layer."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ..config import settings
from ..core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from ..db import models

logger = logging.getLogger(__name__)


class TokenPayload(BaseModel):
    """Internal representation of a decoded JWT."""

    sub: str
    type: str
    exp: datetime | int

    model_config = ConfigDict(extra="ignore")


class AuthService:
    """Service containing user and token helpers."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        """Return a user by email."""

        return self.db.query(models.User).filter(models.User.email == email).first()

    def get_user(self, user_id: str | int) -> Optional[models.User]:
        """Return a user by primary key."""

        return self.db.query(models.User).filter(models.User.id == int(user_id)).first()

    def register_user(self, email: str, password: str) -> models.User:
        """Create a new user after validating uniqueness."""

        if self.get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = models.User(email=email, password_hash=get_password_hash(password))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info("Registered new PulseML user %s", email)
        return user

    def authenticate_user(self, email: str, password: str) -> models.User:
        """Validate user credentials."""

        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        return user

    def create_token_pair(self, user: models.User) -> dict[str, str]:
        """Create access and refresh tokens for a user."""

        subject = str(user.id)
        return {
            "access_token": create_access_token(subject),
            "refresh_token": create_refresh_token(subject),
        }

    def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        """Issue a new access token if the refresh token is valid."""

        payload = self.decode_token(refresh_token)
        if payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )

        user = self.get_user(payload.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        tokens = self.create_token_pair(user)
        return tokens

    @staticmethod
    def decode_token(token: str) -> TokenPayload:
        """Decode a JWT and return the payload."""

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return TokenPayload.model_validate(payload)
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            ) from exc

