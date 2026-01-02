"""Item domain model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Item(BaseModel):
    """Item entity model."""

    id: str = Field(description="Unique identifier")
    name: str = Field(description="Item name")
    description: str | None = Field(default=None, description="Item description")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
