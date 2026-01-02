"""Health check endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from python_template import __version__
from python_template.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    """Health check endpoint for liveness probes."""
    return HealthResponse(status="ok", version=__version__)
