"""Base service class for business logic.

Services orchestrate business logic and delegate data access to repositories.
"""

from __future__ import annotations

from pydantic import BaseModel

from python_template.repositories.base import BaseRepository


class BaseService[T: BaseModel, CreateT: BaseModel, UpdateT: BaseModel]:
    """Base service that delegates data access to a repository.

    Type Parameters:
        T: The entity model type (e.g., Item)
        CreateT: The create request model (e.g., ItemCreate)
        UpdateT: The update request model (e.g., ItemUpdate)

    Services handle:
    - Business logic and validation
    - Orchestration of multiple operations
    - Event emission
    - Authorization checks

    Repositories handle:
    - Data persistence
    - Query execution
    - Transaction management
    """

    def __init__(self, repository: BaseRepository[T, CreateT, UpdateT]) -> None:
        """Initialize service with repository.

        Args:
            repository: The data access repository.
        """
        self._repository = repository

    async def get(self, id: str) -> T | None:
        """Get a single entity by ID.

        Args:
            id: The entity identifier.

        Returns:
            The entity if found, None otherwise.
        """
        return await self._repository.get(id)

    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        """List entities with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of entities.
        """
        return await self._repository.list(skip, limit)

    async def create(self, data: CreateT) -> T:
        """Create a new entity.

        Args:
            data: The creation data.

        Returns:
            The created entity.
        """
        return await self._repository.create(data)

    async def update(self, id: str, data: UpdateT) -> T | None:
        """Update an existing entity.

        Args:
            id: The entity identifier.
            data: The update data.

        Returns:
            The updated entity if found, None otherwise.
        """
        return await self._repository.update(id, data)

    async def delete(self, id: str) -> bool:
        """Delete an entity by ID.

        Args:
            id: The entity identifier.

        Returns:
            True if deleted, False if not found.
        """
        return await self._repository.delete(id)

    async def count(self) -> int:
        """Count total entities.

        Returns:
            Total number of entities.
        """
        return await self._repository.count()

    async def exists(self, id: str) -> bool:
        """Check if an entity exists.

        Args:
            id: The entity identifier.

        Returns:
            True if exists, False otherwise.
        """
        return await self._repository.exists(id)
