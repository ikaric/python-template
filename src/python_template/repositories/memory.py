"""In-memory repository implementation using dict storage.

This implementation is suitable for development, testing, and prototyping.
Replace with a database-backed repository for production use.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, get_args

from pydantic import BaseModel

from python_template.repositories.base import BaseRepository


class InMemoryRepository[T: BaseModel, CreateT: BaseModel, UpdateT: BaseModel](
    BaseRepository[T, CreateT, UpdateT]
):
    """In-memory repository using dict for storage.

    Stores entities in a dictionary with automatic ID generation
    and timestamp management. Lightweight and suitable for templates.

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
        """Initialize empty dict storage."""
        self._data: dict[str, dict[str, Any]] = {}
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
                    self._model_type = model_type  # type: ignore[assignment]
                    return model_type  # type: ignore[return-value]

        msg = "Could not determine model type from generic parameters"
        raise TypeError(msg)

    def _dict_to_model(self, data: dict[str, Any]) -> T:
        """Convert a dict to a Pydantic model.

        Args:
            data: A dictionary representing a single entity.

        Returns:
            The entity as a Pydantic model instance.
        """
        model_type = self._get_model_type()
        return model_type.model_validate(data)

    async def get(self, id: str) -> T | None:
        """Get a single entity by ID.

        Args:
            id: The entity identifier.

        Returns:
            The entity if found, None otherwise.
        """
        data = self._data.get(id)
        if data is None:
            return None
        return self._dict_to_model(data)

    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        """List entities with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of entities sorted by created_at descending (newest first).
        """
        if not self._data:
            return []

        # Sort by created_at descending (newest first)
        sorted_items = sorted(
            self._data.values(),
            key=lambda x: x.get("created_at", datetime.min.replace(tzinfo=UTC)),
            reverse=True,
        )

        # Apply pagination
        paginated = sorted_items[skip : skip + limit]
        return [self._dict_to_model(item) for item in paginated]

    async def create(self, data: CreateT) -> T:
        """Create a new entity.

        Automatically generates ID and timestamps.

        Args:
            data: The creation data.

        Returns:
            The created entity with generated ID and timestamps.
        """
        now = datetime.now(UTC)
        entity_id = str(uuid.uuid4())
        entity_dict = {
            "id": entity_id,
            **data.model_dump(),
            "created_at": now,
            "updated_at": now,
        }

        self._data[entity_id] = entity_dict
        return self._dict_to_model(entity_dict)

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
        if id not in self._data:
            return None

        # Get update data excluding unset fields
        update_dict = data.model_dump(exclude_unset=True)

        if update_dict:
            update_dict["updated_at"] = datetime.now(UTC)
            self._data[id].update(update_dict)

        return self._dict_to_model(self._data[id])

    async def delete(self, id: str) -> bool:
        """Delete an entity by ID.

        Args:
            id: The entity identifier.

        Returns:
            True if deleted, False if not found.
        """
        if id not in self._data:
            return False

        del self._data[id]
        return True

    async def count(self) -> int:
        """Count total entities.

        Returns:
            Total number of entities.
        """
        return len(self._data)

    async def exists(self, id: str) -> bool:
        """Check if an entity exists.

        Args:
            id: The entity identifier.

        Returns:
            True if exists, False otherwise.
        """
        return id in self._data

    async def clear(self) -> None:
        """Remove all entities.

        Useful for testing and development.
        """
        self._data.clear()
