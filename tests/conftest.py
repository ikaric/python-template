"""Pytest fixtures for testing."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from python_template.api.app import create_app
from python_template.api.schemas import ItemCreate


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_item_data() -> ItemCreate:
    """Sample item data for testing."""
    return ItemCreate(
        name="Test Item",
        description="A test item for unit testing",
    )
