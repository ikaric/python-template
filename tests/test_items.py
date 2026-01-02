"""Tests for items endpoints and service."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from python_template.api.schemas import ItemCreate, ItemUpdate
from python_template.services import ItemService


class TestItemService:
    """Unit tests for ItemService."""

    @pytest.fixture
    def service(self) -> ItemService:
        """Create a fresh ItemService instance."""
        return ItemService()

    @pytest.mark.asyncio
    async def test_create_item(self, service: ItemService) -> None:
        """Test creating an item."""
        data = ItemCreate(name="Test", description="Test description")
        item = await service.create(data)

        assert item.id is not None
        assert item.name == "Test"
        assert item.description == "Test description"
        assert item.created_at is not None
        assert item.updated_at is not None

    @pytest.mark.asyncio
    async def test_get_item(self, service: ItemService) -> None:
        """Test getting an item by ID."""
        data = ItemCreate(name="Test")
        created = await service.create(data)

        item = await service.get(created.id)
        assert item is not None
        assert item.id == created.id
        assert item.name == "Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_item(self, service: ItemService) -> None:
        """Test getting a nonexistent item returns None."""
        item = await service.get("nonexistent-id")
        assert item is None

    @pytest.mark.asyncio
    async def test_list_items(self, service: ItemService) -> None:
        """Test listing items."""
        await service.create(ItemCreate(name="Item 1"))
        await service.create(ItemCreate(name="Item 2"))

        items = await service.list()
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_list_items_pagination(self, service: ItemService) -> None:
        """Test listing items with pagination."""
        for i in range(5):
            await service.create(ItemCreate(name=f"Item {i}"))

        items = await service.list(skip=2, limit=2)
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_update_item(self, service: ItemService) -> None:
        """Test updating an item."""
        created = await service.create(ItemCreate(name="Original"))
        updated = await service.update(created.id, ItemUpdate(name="Updated"))

        assert updated is not None
        assert updated.name == "Updated"
        assert updated.updated_at > created.updated_at

    @pytest.mark.asyncio
    async def test_delete_item(self, service: ItemService) -> None:
        """Test deleting an item."""
        created = await service.create(ItemCreate(name="To Delete"))

        deleted = await service.delete(created.id)
        assert deleted is True

        item = await service.get(created.id)
        assert item is None


class TestItemEndpoints:
    """Integration tests for item API endpoints."""

    def test_list_items_empty(self, client: TestClient) -> None:
        """Test listing items when empty."""
        response = client.get("/v1/items")

        assert response.status_code == 200
        assert response.json() == []

    def test_create_item(self, client: TestClient) -> None:
        """Test creating an item via API."""
        response = client.post(
            "/v1/items",
            json={"name": "API Test", "description": "Created via API"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test"
        assert data["description"] == "Created via API"
        assert "id" in data

    def test_create_item_validation_error(self, client: TestClient) -> None:
        """Test creating an item with invalid data."""
        response = client.post(
            "/v1/items",
            json={"name": ""},  # Empty name should fail validation
        )

        assert response.status_code == 422

    def test_get_item(self, client: TestClient) -> None:
        """Test getting an item by ID."""
        # Create an item first
        create_response = client.post("/v1/items", json={"name": "Get Test"})
        item_id = create_response.json()["id"]

        # Get the item
        response = client.get(f"/v1/items/{item_id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Get Test"

    def test_get_nonexistent_item(self, client: TestClient) -> None:
        """Test getting a nonexistent item returns 404."""
        response = client.get("/v1/items/nonexistent-id")

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "not_found"

    def test_update_item(self, client: TestClient) -> None:
        """Test updating an item."""
        # Create an item first
        create_response = client.post("/v1/items", json={"name": "Original"})
        item_id = create_response.json()["id"]

        # Update the item
        response = client.put(f"/v1/items/{item_id}", json={"name": "Updated"})

        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    def test_delete_item(self, client: TestClient) -> None:
        """Test deleting an item."""
        # Create an item first
        create_response = client.post("/v1/items", json={"name": "To Delete"})
        item_id = create_response.json()["id"]

        # Delete the item
        response = client.delete(f"/v1/items/{item_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/v1/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_item(self, client: TestClient) -> None:
        """Test deleting a nonexistent item returns 404."""
        response = client.delete("/v1/items/nonexistent-id")

        assert response.status_code == 404
