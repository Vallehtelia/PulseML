"""Application configuration for PulseML."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration object for PulseML."""

    APP_NAME: str = "PulseML Backend"
    API_V1_PREFIX: str = "/api"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/pulseml"
    REDIS_URL: str = "redis://redis:6379/0"
    DATA_DIR: str = "/app/data"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(1)
def get_settings() -> "Settings":
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()


