"""Item service with in-memory storage.

Example service implementation demonstrating the CRUD pattern.
Easily swappable for database-backed storage.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from python_template.api.exceptions import NotFoundError
from python_template.api.schemas import ItemCreate, ItemUpdate
from python_template.models import Item
from python_template.services.base import BaseService


class ItemService(BaseService[Item, ItemCreate, ItemUpdate]):
    """Item service with in-memory storage.

    This is an example implementation using a simple dict for storage.
    Replace with database operations for production use.
    """

    def __init__(self) -> None:
        self._storage: dict[str, Item] = {}

    async def get(self, id: str) -> Item | None:
        """Get an item by ID."""
        return self._storage.get(id)

    async def get_or_raise(self, id: str) -> Item:
        """Get an item by ID or raise NotFoundError."""
        item = await self.get(id)
        if item is None:
            raise NotFoundError(resource="Item", identifier=id)
        return item

    async def list(self, skip: int = 0, limit: int = 100) -> list[Item]:
        """List all items with pagination."""
        items = list(self._storage.values())
        return items[skip : skip + limit]

    async def create(self, data: ItemCreate) -> Item:
        """Create a new item."""
        now = datetime.now(UTC)
        item = Item(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            created_at=now,
            updated_at=now,
        )
        self._storage[item.id] = item
        return item

    async def update(self, id: str, data: ItemUpdate) -> Item | None:
        """Update an existing item."""
        item = self._storage.get(id)
        if item is None:
            return None

        # Apply updates
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(UTC)
            updated_item = item.model_copy(update=update_data)
            self._storage[id] = updated_item
            return updated_item

        return item

    async def update_or_raise(self, id: str, data: ItemUpdate) -> Item:
        """Update an item or raise NotFoundError."""
        item = await self.update(id, data)
        if item is None:
            raise NotFoundError(resource="Item", identifier=id)
        return item

    async def delete(self, id: str) -> bool:
        """Delete an item by ID."""
        if id in self._storage:
            del self._storage[id]
            return True
        return False

    async def delete_or_raise(self, id: str) -> None:
        """Delete an item or raise NotFoundError."""
        if not await self.delete(id):
            raise NotFoundError(resource="Item", identifier=id)
