"""Pytest fixtures for testing."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from python_template.api.app import create_app
from python_template.api.schemas import ItemCreate
from python_template.repositories import ItemRepository
from python_template.services import ItemService


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def item_repository() -> ItemRepository:
    """Create a fresh ItemRepository for testing."""
    return ItemRepository()


@pytest.fixture
def item_service(item_repository: ItemRepository) -> ItemService:
    """Create a fresh ItemService with repository for testing."""
    return ItemService(item_repository)


@pytest.fixture
def sample_item_data() -> ItemCreate:
    """Sample item data for testing."""
    return ItemCreate(
        name="Test Item",
        description="A test item for unit testing",
    )
