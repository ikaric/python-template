"""In-memory repository implementation using pandas DataFrame.

This implementation is suitable for development, testing, and prototyping.
Replace with a database-backed repository for production use.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, get_args

import pandas as pd
from pydantic import BaseModel

from python_template.repositories.base import BaseRepository


class InMemoryRepository[T: BaseModel, CreateT: BaseModel, UpdateT: BaseModel](
    BaseRepository[T, CreateT, UpdateT]
):
    """In-memory repository using pandas DataFrame for storage.

    Stores entities in a pandas DataFrame with automatic ID generation
    and timestamp management. Thread-safe for basic operations.

    Type Parameters:
        T: The entity model type (e.g., Item)
        CreateT: The create request model (e.g., ItemCreate)
        UpdateT: The update request model (e.g., ItemUpdate)

    Example:
        >>> repo = InMemoryRepository[Item, ItemCreate, ItemUpdate]()
        >>> item = await repo.create(ItemCreate(name="Test"))
        >>> items = await repo.list()
    """

    def __init__(self) -> None:
        """Initialize empty DataFrame storage."""
        self._df: pd.DataFrame = pd.DataFrame()
        self._model_type: type[T] | None = None

    def _get_model_type(self) -> type[T]:
        """Get the entity model type from generic parameters.

        Returns:
            The Pydantic model class for the entity type.

        Raises:
            TypeError: If model type cannot be determined.
        """
        if self._model_type is not None:
            return self._model_type

        # Get the type from __orig_bases__ for generic subclasses
        for base in getattr(self.__class__, "__orig_bases__", []):
            args = get_args(base)
            if args and len(args) >= 1:
                model_type = args[0]
                if isinstance(model_type, type) and issubclass(model_type, BaseModel):
                    self._model_type = model_type
                    return model_type

        msg = "Could not determine model type from generic parameters"
        raise TypeError(msg)

    def _row_to_model(self, row: pd.Series) -> T:  # type: ignore[type-arg]
        """Convert a DataFrame row to a Pydantic model.

        Args:
            row: A pandas Series representing a single entity.

        Returns:
            The entity as a Pydantic model instance.
        """
        model_type = self._get_model_type()
        return model_type.model_validate(row.to_dict())

    def _model_to_dict(self, model: T) -> dict[str, Any]:
        """Convert a Pydantic model to a dictionary for DataFrame storage.

        Args:
            model: The Pydantic model instance.

        Returns:
            Dictionary representation suitable for DataFrame.
        """
        return model.model_dump()

    async def get(self, id: str) -> T | None:
        """Get a single entity by ID.

        Args:
            id: The entity identifier.

        Returns:
            The entity if found, None otherwise.
        """
        if self._df.empty:
            return None

        mask = self._df["id"] == id
        if not mask.any():
            return None

        row = self._df.loc[mask].iloc[0]
        return self._row_to_model(row)

    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        """List entities with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of entities.
        """
        if self._df.empty:
            return []

        # Sort by created_at descending (newest first)
        sorted_df = self._df.sort_values("created_at", ascending=False)
        paginated = sorted_df.iloc[skip : skip + limit]

        return [self._row_to_model(row) for _, row in paginated.iterrows()]

    async def create(self, data: CreateT) -> T:
        """Create a new entity.

        Automatically generates ID and timestamps.

        Args:
            data: The creation data.

        Returns:
            The created entity with generated ID and timestamps.
        """
        now = datetime.now(UTC)
        entity_dict = {
            "id": str(uuid.uuid4()),
            **data.model_dump(),
            "created_at": now,
            "updated_at": now,
        }

        # Create or append to DataFrame
        new_row = pd.DataFrame([entity_dict])
        if self._df.empty:
            self._df = new_row
        else:
            self._df = pd.concat([self._df, new_row], ignore_index=True)

        model_type = self._get_model_type()
        return model_type.model_validate(entity_dict)

    async def update(self, id: str, data: UpdateT) -> T | None:
        """Update an existing entity.

        Only updates fields that are explicitly set in the update data.
        Automatically updates the updated_at timestamp.

        Args:
            id: The entity identifier.
            data: The update data.

        Returns:
            The updated entity if found, None otherwise.
        """
        if self._df.empty:
            return None

        mask = self._df["id"] == id
        if not mask.any():
            return None

        # Get update data excluding unset fields
        update_dict = data.model_dump(exclude_unset=True)

        if update_dict:
            update_dict["updated_at"] = datetime.now(UTC)
            for key, value in update_dict.items():
                self._df.loc[mask, key] = value

        row = self._df.loc[mask].iloc[0]
        return self._row_to_model(row)

    async def delete(self, id: str) -> bool:
        """Delete an entity by ID.

        Args:
            id: The entity identifier.

        Returns:
            True if deleted, False if not found.
        """
        if self._df.empty:
            return False

        mask = self._df["id"] == id
        if not mask.any():
            return False

        self._df = self._df[~mask].reset_index(drop=True)
        return True

    async def count(self) -> int:
        """Count total entities.

        Returns:
            Total number of entities.
        """
        return len(self._df)

    async def exists(self, id: str) -> bool:
        """Check if an entity exists.

        Args:
            id: The entity identifier.

        Returns:
            True if exists, False otherwise.
        """
        if self._df.empty:
            return False
        return bool((self._df["id"] == id).any())

    async def clear(self) -> None:
        """Remove all entities.

        Useful for testing and development.
        """
        self._df = pd.DataFrame()
