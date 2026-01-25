"""Item service with business logic.

Service layer for Item entities, handling business rules and validation.
Data access is delegated to the ItemRepository.
"""

from __future__ import annotations

from python_template.api.exceptions import NotFoundError
from python_template.api.schemas import ItemCreate, ItemUpdate
from python_template.models import Item
from python_template.repositories import ItemRepository
from python_template.services.base import BaseService


class ItemService(BaseService[Item, ItemCreate, ItemUpdate]):
    """Item service handling business logic.

    Delegates data access to ItemRepository while providing:
    - Convenience methods that raise exceptions
    - Business validation
    - Future: authorization, events, caching

    Example:
        >>> repo = ItemRepository()
        >>> service = ItemService(repo)
        >>> item = await service.create(ItemCreate(name="Test"))
        >>> item = await service.get_or_raise(item.id)
    """

    def __init__(self, repository: ItemRepository) -> None:
        """Initialize service with item repository.

        Args:
            repository: The item data access repository.
        """
        super().__init__(repository)
        self._item_repo = repository

    async def get_or_raise(self, id: str) -> Item:
        """Get an item by ID or raise NotFoundError.

        Args:
            id: The item identifier.

        Returns:
            The item.

        Raises:
            NotFoundError: If item not found.
        """
        item = await self.get(id)
        if item is None:
            raise NotFoundError(resource="Item", identifier=id)
        return item

    async def update_or_raise(self, id: str, data: ItemUpdate) -> Item:
        """Update an item or raise NotFoundError.

        Args:
            id: The item identifier.
            data: The update data.

        Returns:
            The updated item.

        Raises:
            NotFoundError: If item not found.
        """
        item = await self.update(id, data)
        if item is None:
            raise NotFoundError(resource="Item", identifier=id)
        return item

    async def delete_or_raise(self, id: str) -> None:
        """Delete an item or raise NotFoundError.

        Args:
            id: The item identifier.

        Raises:
            NotFoundError: If item not found.
        """
        deleted = await self.delete(id)
        if not deleted:
            raise NotFoundError(resource="Item", identifier=id)

    async def find_by_name(self, name: str) -> list[Item]:
        """Find items by name (case-insensitive partial match).

        Args:
            name: The name to search for.

        Returns:
            List of matching items.
        """
        return await self._item_repo.find_by_name(name)
