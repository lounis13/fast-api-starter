from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.v1.routers import router as api_v1_router
from app.api.exception_handlers import register_exception_handlers
from app.config.settings import Settings, get_settings
from app.infrastructure.logging.config import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    settings: Settings = get_settings()
    configure_logging(settings)
    logging.getLogger(__name__).info("Application starting", extra={"env": settings.env})
    yield
    # Shutdown
    logging.getLogger(__name__).info("Application shutdown")


def create_app() -> FastAPI:
    settings: Settings = get_settings()

    app = FastAPI(
        title=settings.name,
        version=settings.version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        description=(
            "Starter FastAPI project with Clean Architecture, SOLID, async httpx calls via services/adapters,"
            " environment-driven logging, and full test layers (unit, integration, e2e, BDD)."
        ),
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    app.include_router(api_v1_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings: Settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
