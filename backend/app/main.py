"""Entry point for the PulseML FastAPI application."""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .config import settings
from .db.session import SessionLocal
from .models_registry.registry import seed_default_templates

logger = logging.getLogger("pulseml.app")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    app = FastAPI(
        title="PulseML",
        description="PulseML Backend API",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event() -> None:
        """Perform startup tasks like directory creation and seeding."""

        Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
        with SessionLocal() as session:
            seed_default_templates(session)
        logger.info("PulseML application startup complete")

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Simple health check endpoint."""

        return {"status": "ok"}

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_application()


def run() -> None:  # pragma: no cover - convenience runner
    """Run the FastAPI app with Uvicorn."""

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


