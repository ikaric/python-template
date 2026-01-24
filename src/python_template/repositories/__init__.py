"""Repository layer for data access.

The repository pattern separates data access logic from business logic,
making it easy to swap storage backends (in-memory, MongoDB, PostgreSQL, etc.).
"""

from __future__ import annotations

from python_template.repositories.base import BaseRepository
from python_template.repositories.items import ItemRepository
from python_template.repositories.memory import InMemoryRepository

__all__ = [
    "BaseRepository",
    "InMemoryRepository",
    "ItemRepository",
]
