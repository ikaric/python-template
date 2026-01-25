"""Common API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Service status")
    version: str = Field(description="Application version")
