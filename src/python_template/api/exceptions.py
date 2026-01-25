"""Centralized exception handling.

Provides consistent JSON error responses across the API.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from python_template.api.schemas import ErrorDetail, ErrorResponse


class AppException(Exception):
    """Base application exception with structured error response.

    All custom exceptions should inherit from this class.
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

    def to_response(self) -> ErrorResponse:
        """Convert exception to ErrorResponse model."""
        return ErrorResponse(
            error=ErrorDetail(
                code=self.code,
                message=self.message,
                details=self.details,
            )
        )


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(
        self,
        resource: str,
        identifier: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            code="not_found",
            message=message,
            status_code=404,
            details=details,
        )


class ValidationError(AppException):
    """Validation error."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="validation_error",
            message=message,
            status_code=422,
            details=details,
        )


class ConflictError(AppException):
    """Resource conflict error (e.g., duplicate)."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="conflict",
            message=message,
            status_code=409,
            details=details,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException and return structured JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response().model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with a generic error response."""
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="internal_error",
            message="An unexpected error occurred",
            details=None,
        )
    )
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    # Optionally catch all unhandled exceptions (comment out for debugging)
    # app.add_exception_handler(Exception, generic_exception_handler)
