"""Dependency injection providers for FastAPI.

This module provides typed dependency providers that integrate with FastAPI's
DI system while maintaining explicit lifecycle control via the lifespan.

Pattern:
    1. AppState holds all singleton services (initialized in lifespan)
    2. get_app_state() retrieves typed state from request
    3. Individual providers (get_item_service, etc.) extract specific services

This gives you:
    - Full type safety (no untyped app.state access in routes)
    - Explicit dependency graph visible in function signatures
    - Singleton lifecycle controlled by lifespan
    - Easy testing via dependency overrides
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

if TYPE_CHECKING:
    from python_template.repositories import ItemRepository
    from python_template.services import ItemService


@dataclass
class AppState:
    """Typed container for application-wide singleton services.

    All services are initialized once during application lifespan startup
    and shared across all requests. This pattern is ideal for:
    - Database connection pools
    - ML model instances (avoids reloading per request)
    - Cached configuration
    - Service singletons

    Example:
        # In lifespan.py
        state = AppState(
            item_repository=ItemRepository(),
            item_service=ItemService(item_repository),
        )
        app.state.container = state

        # In routes (via dependency injection)
        async def create_item(service: ItemServiceDep): ...
    """

    item_repository: ItemRepository
    item_service: ItemService


def get_app_state(request: Request) -> AppState:
    """Extract typed AppState from the request.

    This is the single point where we access app.state, providing
    type safety for all downstream dependencies.

    Args:
        request: The FastAPI request object.

    Returns:
        The typed AppState container.

    Raises:
        AttributeError: If state not initialized (lifespan not configured).
    """
    return request.app.state.container  # type: ignore[no-any-return]


def get_item_repository(
    state: Annotated[AppState, Depends(get_app_state)],
) -> ItemRepository:
    """Provide ItemRepository from application state.

    Args:
        state: The typed application state container.

    Returns:
        The item repository singleton.
    """
    return state.item_repository


def get_item_service(
    state: Annotated[AppState, Depends(get_app_state)],
) -> ItemService:
    """Provide ItemService from application state.

    Args:
        state: The typed application state container.

    Returns:
        The item service singleton.
    """
    return state.item_service


# Type aliases for cleaner route signatures
AppStateDep = Annotated[AppState, Depends(get_app_state)]
ItemRepositoryDep = Annotated["ItemRepository", Depends(get_item_repository)]
ItemServiceDep = Annotated["ItemService", Depends(get_item_service)]
