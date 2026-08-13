"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import api_v1_router
from app.config.settings import get_settings
from app.core.logging import configure_logging
from app.middleware.error_handler import register_error_handlers
from app.middleware.request_context import RequestContextMiddleware
from app.shared.database.base import Base
from app.shared.database.session import dispose_engine, get_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create tables on startup for local dev; release resources on shutdown."""
    settings = get_settings()
    if settings.database_url.startswith("sqlite"):
        async with get_engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    """Create and configure the RepoMind ASGI application."""
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Repository Intelligence Platform API",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    register_error_handlers(app)
    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return app
