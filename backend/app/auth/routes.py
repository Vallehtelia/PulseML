"""Auth API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..db import models
from . import schemas
from .service import AuthService

router = APIRouter()


@router.post("/register", response_model=schemas.UserRead, status_code=201)
async def register_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
) -> schemas.UserRead:
    """Register a new PulseML user."""

    service = AuthService(db)
    user = service.register_user(email=payload.email, password=payload.password)
    return schemas.UserRead.model_validate(user)


@router.post("/login", response_model=schemas.TokenPair)
async def login(
    payload: schemas.UserLogin,
    db: Session = Depends(get_db),
) -> schemas.TokenPair:
    """Authenticate a user and return tokens."""

    service = AuthService(db)
    user = service.authenticate_user(payload.email, payload.password)
    tokens = service.create_token_pair(user)
    return schemas.TokenPair(**tokens)


@router.post("/refresh", response_model=schemas.TokenPair)
async def refresh_tokens(
    payload: schemas.TokenRefresh,
    db: Session = Depends(get_db),
) -> schemas.TokenPair:
    """Issue a new access token pair."""

    service = AuthService(db)
    tokens = service.refresh_access_token(payload.refresh_token)
    return schemas.TokenPair(**tokens)


@router.get("/me", response_model=schemas.UserRead)
async def read_me(current_user: models.User = Depends(get_current_user)) -> schemas.UserRead:
    """Return the authenticated user's profile."""

    return schemas.UserRead.model_validate(current_user)

