"""FastAPI application factory.

Creates and configures the FastAPI application with:
- Lifespan context for startup/shutdown
- Exception handlers
- API routes
"""

from __future__ import annotations

from fastapi import FastAPI

from python_template import __version__
from python_template.api.exceptions import register_exception_handlers
from python_template.api.lifespan import lifespan
from python_template.api.routes import build_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="python-template",
        description="A reusable Python project template with FastAPI",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Include API routes
    app.include_router(build_router())

    return app
