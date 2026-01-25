"""Tests for items repository, service, and endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from python_template.api.schemas import ItemCreate, ItemUpdate
from python_template.repositories import ItemRepository
from python_template.services import ItemService


class TestItemRepository:
    """Unit tests for ItemRepository (data layer)."""

    @pytest.fixture
    def repository(self) -> ItemRepository:
        """Create a fresh ItemRepository instance."""
        return ItemRepository()

    @pytest.mark.asyncio
    async def test_create_item(self, repository: ItemRepository) -> None:
        """Test creating an item in the repository."""
        data = ItemCreate(name="Test", description="Test description")
        item = await repository.create(data)

        assert item.id is not None
        assert item.name == "Test"
        assert item.description == "Test description"
        assert item.created_at is not None
        assert item.updated_at is not None

    @pytest.mark.asyncio
    async def test_get_item(self, repository: ItemRepository) -> None:
        """Test getting an item by ID from repository."""
        data = ItemCreate(name="Test")
        created = await repository.create(data)

        item = await repository.get(created.id)
        assert item is not None
        assert item.id == created.id
        assert item.name == "Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_item(self, repository: ItemRepository) -> None:
        """Test getting a nonexistent item returns None."""
        item = await repository.get("nonexistent-id")
        assert item is None

    @pytest.mark.asyncio
    async def test_list_items(self, repository: ItemRepository) -> None:
        """Test listing items from repository."""
        await repository.create(ItemCreate(name="Item 1"))
        await repository.create(ItemCreate(name="Item 2"))

        items = await repository.list()
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_list_items_pagination(self, repository: ItemRepository) -> None:
        """Test listing items with pagination."""
        for i in range(5):
            await repository.create(ItemCreate(name=f"Item {i}"))

        items = await repository.list(skip=2, limit=2)
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_update_item(self, repository: ItemRepository) -> None:
        """Test updating an item in repository."""
        created = await repository.create(ItemCreate(name="Original"))
        updated = await repository.update(created.id, ItemUpdate(name="Updated"))

        assert updated is not None
        assert updated.name == "Updated"
        assert updated.updated_at > created.updated_at

    @pytest.mark.asyncio
    async def test_delete_item(self, repository: ItemRepository) -> None:
        """Test deleting an item from repository."""
        created = await repository.create(ItemCreate(name="To Delete"))

        deleted = await repository.delete(created.id)
        assert deleted is True

        item = await repository.get(created.id)
        assert item is None

    @pytest.mark.asyncio
    async def test_count_items(self, repository: ItemRepository) -> None:
        """Test counting items in repository."""
        assert await repository.count() == 0

        await repository.create(ItemCreate(name="Item 1"))
        await repository.create(ItemCreate(name="Item 2"))

        assert await repository.count() == 2

    @pytest.mark.asyncio
    async def test_exists(self, repository: ItemRepository) -> None:
        """Test checking if item exists."""
        created = await repository.create(ItemCreate(name="Test"))

        assert await repository.exists(created.id) is True
        assert await repository.exists("nonexistent-id") is False

    @pytest.mark.asyncio
    async def test_clear(self, repository: ItemRepository) -> None:
        """Test clearing all items from repository."""
        await repository.create(ItemCreate(name="Item 1"))
        await repository.create(ItemCreate(name="Item 2"))

        await repository.clear()

        assert await repository.count() == 0

    @pytest.mark.asyncio
    async def test_find_by_name(self, repository: ItemRepository) -> None:
        """Test finding items by name."""
        await repository.create(ItemCreate(name="Apple"))
        await repository.create(ItemCreate(name="Banana"))
        await repository.create(ItemCreate(name="Pineapple"))

        results = await repository.find_by_name("apple")
        assert len(results) == 2  # Apple and Pineapple


class TestItemService:
    """Unit tests for ItemService (business layer)."""

    @pytest.mark.asyncio
    async def test_create_item(self, item_service: ItemService) -> None:
        """Test creating an item through service."""
        data = ItemCreate(name="Test", description="Test description")
        item = await item_service.create(data)

        assert item.id is not None
        assert item.name == "Test"
        assert item.description == "Test description"

    @pytest.mark.asyncio
    async def test_get_or_raise_success(self, item_service: ItemService) -> None:
        """Test get_or_raise returns item when found."""
        created = await item_service.create(ItemCreate(name="Test"))
        item = await item_service.get_or_raise(created.id)

        assert item.id == created.id

    @pytest.mark.asyncio
    async def test_get_or_raise_not_found(self, item_service: ItemService) -> None:
        """Test get_or_raise raises NotFoundError."""
        from python_template.api.exceptions import NotFoundError

        with pytest.raises(NotFoundError):
            await item_service.get_or_raise("nonexistent-id")

    @pytest.mark.asyncio
    async def test_update_or_raise_success(self, item_service: ItemService) -> None:
        """Test update_or_raise updates item when found."""
        created = await item_service.create(ItemCreate(name="Original"))
        updated = await item_service.update_or_raise(
            created.id, ItemUpdate(name="Updated")
        )

        assert updated.name == "Updated"

    @pytest.mark.asyncio
    async def test_update_or_raise_not_found(self, item_service: ItemService) -> None:
        """Test update_or_raise raises NotFoundError."""
        from python_template.api.exceptions import NotFoundError

        with pytest.raises(NotFoundError):
            await item_service.update_or_raise(
                "nonexistent-id", ItemUpdate(name="Updated")
            )

    @pytest.mark.asyncio
    async def test_delete_or_raise_success(self, item_service: ItemService) -> None:
        """Test delete_or_raise deletes item when found."""
        created = await item_service.create(ItemCreate(name="To Delete"))
        await item_service.delete_or_raise(created.id)

        item = await item_service.get(created.id)
        assert item is None

    @pytest.mark.asyncio
    async def test_delete_or_raise_not_found(self, item_service: ItemService) -> None:
        """Test delete_or_raise raises NotFoundError."""
        from python_template.api.exceptions import NotFoundError

        with pytest.raises(NotFoundError):
            await item_service.delete_or_raise("nonexistent-id")


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
