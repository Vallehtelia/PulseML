"""Auth schemas for PulseML."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Schema for registering a new user."""

    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for logging in."""

    email: EmailStr
    password: str


class TokenPair(BaseModel):
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Refresh token payload."""

    refresh_token: str


class UserRead(BaseModel):
    """Public user representation."""

    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

