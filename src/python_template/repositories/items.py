"""Item repository implementation.

Provides data access for Item entities using in-memory DataFrame storage.
"""

from __future__ import annotations

from python_template.api.schemas import ItemCreate, ItemUpdate
from python_template.models import Item
from python_template.repositories.memory import InMemoryRepository


class ItemRepository(InMemoryRepository[Item, ItemCreate, ItemUpdate]):
    """Item repository with DataFrame-based storage.

    Inherits all CRUD operations from InMemoryRepository.
    Extend this class to add item-specific query methods.

    Example:
        >>> repo = ItemRepository()
        >>> item = await repo.create(ItemCreate(name="Test"))
        >>> items = await repo.list(skip=0, limit=10)

    To swap to a database backend:
        1. Create ItemMongoRepository or ItemSQLRepository
        2. Implement BaseRepository interface
        3. Change ItemRepository to inherit from the new implementation
    """

    async def find_by_name(self, name: str) -> list[Item]:
        """Find items by name (case-insensitive partial match).

        Args:
            name: The name to search for.

        Returns:
            List of matching items.
        """
        if self._df.empty:
            return []

        mask = self._df["name"].str.contains(name, case=False, na=False)
        return [self._row_to_model(row) for _, row in self._df[mask].iterrows()]
