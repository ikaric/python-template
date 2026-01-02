"""Item CRUD endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from python_template.api.schemas import ItemCreate, ItemUpdate
from python_template.models import Item
from python_template.services import ItemService

router = APIRouter(prefix="/items", tags=["items"])


def get_item_service(request: Request) -> ItemService:
    """Dependency to get ItemService from app state."""
    return request.app.state.item_service


ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


@router.get("", response_model=list[Item])
async def list_items(
    service: ItemServiceDep,
    skip: Annotated[int, Query(ge=0, description="Records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description="Max records")] = 100,
) -> list[Item]:
    """List all items with pagination."""
    return await service.list(skip=skip, limit=limit)


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: str,
    service: ItemServiceDep,
) -> Item:
    """Get a single item by ID."""
    return await service.get_or_raise(item_id)


@router.post("", response_model=Item, status_code=201)
async def create_item(
    data: ItemCreate,
    service: ItemServiceDep,
) -> Item:
    """Create a new item."""
    return await service.create(data)


@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: str,
    data: ItemUpdate,
    service: ItemServiceDep,
) -> Item:
    """Update an existing item."""
    return await service.update_or_raise(item_id, data)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: str,
    service: ItemServiceDep,
) -> None:
    """Delete an item."""
    await service.delete_or_raise(item_id)
