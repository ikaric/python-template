"""Item API schemas - request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Item creation request."""

    name: str = Field(min_length=1, max_length=255, description="Item name")
    description: str | None = Field(
        default=None, max_length=1000, description="Item description"
    )


class ItemUpdate(BaseModel):
    """Item update request."""

    name: str | None = Field(
        default=None, min_length=1, max_length=255, description="Item name"
    )
    description: str | None = Field(
        default=None, max_length=1000, description="Item description"
    )
