"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings
from .base import Base

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


def get_engine():
    """Expose the configured engine for migrations."""

    return engine


def init_db() -> None:
    """Create tables in development environments when needed."""

    Base.metadata.create_all(bind=engine)

