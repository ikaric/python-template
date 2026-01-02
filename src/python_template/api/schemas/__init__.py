"""API schemas package - request/response models."""

from python_template.api.schemas.common import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
)
from python_template.api.schemas.items import ItemCreate, ItemUpdate

__all__ = [
    # Common
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    # Items
    "ItemCreate",
    "ItemUpdate",
]
