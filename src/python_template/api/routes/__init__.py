"""API route modules."""

from __future__ import annotations

from fastapi import APIRouter

from python_template.api.routes.health import router as health_router
from python_template.api.routes.items import router as items_router


def build_router() -> APIRouter:
    """Build the main API router with all routes mounted."""
    router = APIRouter()

    # Health check at root level
    router.include_router(health_router)

    # Versioned API routes
    router.include_router(items_router, prefix="/v1")

    return router
