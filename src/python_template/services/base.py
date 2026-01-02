"""Base service class with generic CRUD operations.

Provides a type-safe foundation for service implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseService[T: BaseModel, CreateT: BaseModel, UpdateT: BaseModel](ABC):
    """Abstract base service with CRUD method signatures.

    Type Parameters:
        T: The entity model type (e.g., Item)
        CreateT: The create request model (e.g., ItemCreate)
        UpdateT: The update request model (e.g., ItemUpdate)
    """

    @abstractmethod
    async def get(self, id: str) -> T | None:
        """Get a single entity by ID.

        Args:
            id: The entity identifier.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        """List entities with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of entities.
        """
        ...

    @abstractmethod
    async def create(self, data: CreateT) -> T:
        """Create a new entity.

        Args:
            data: The creation data.

        Returns:
            The created entity.
        """
        ...

    @abstractmethod
    async def update(self, id: str, data: UpdateT) -> T | None:
        """Update an existing entity.

        Args:
            id: The entity identifier.
            data: The update data.

        Returns:
            The updated entity if found, None otherwise.
        """
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an entity by ID.

        Args:
            id: The entity identifier.

        Returns:
            True if deleted, False if not found.
        """
        ...
