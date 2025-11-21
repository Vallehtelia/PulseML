"""Aggregate API routers for PulseML."""

from fastapi import APIRouter

from ..auth.routes import router as auth_router
from ..datasets.routes import router as datasets_router
from ..models_registry.routes import router as models_registry_router
from ..training.routes import router as training_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(datasets_router, prefix="/datasets", tags=["datasets"])
api_router.include_router(training_router, prefix="/training-runs", tags=["training"])
api_router.include_router(
    models_registry_router, prefix="/models", tags=["model-templates"]
)

