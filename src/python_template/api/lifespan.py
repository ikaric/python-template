"""FastAPI lifespan context manager for startup/shutdown.

Initializes repositories and services, storing them in app.state for DI.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from python_template.logging import configure_logging, get_logger
from python_template.repositories import ItemRepository
from python_template.services import ItemService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle.

    Startup:
        - Configure logging
        - Initialize repositories (data layer)
        - Initialize services (business layer)
        - Store in app.state for dependency injection

    Shutdown:
        - Cleanup resources (database connections, etc.)

    The repository pattern allows easy swapping of storage backends:
        - Development: InMemoryRepository (pandas DataFrame)
        - Production: MongoRepository, PostgresRepository, etc.
    """
    # Configure logging first
    configure_logging()
    log = get_logger("python_template.startup")

    log.info("Application starting up...")

    # Initialize repositories (data layer)
    # Swap these for database-backed repositories in production
    item_repository = ItemRepository()
    log.debug("Initialized item repository (in-memory)")

    # Initialize services (business layer)
    item_service = ItemService(item_repository)
    log.debug("Initialized item service")

    # Store in app.state for dependency injection
    # Both repository and service are available if needed
    app.state.item_repository = item_repository
    app.state.item_service = item_service

    log.info("Application initialized successfully")

    yield

    # Shutdown
    log.info("Application shutting down...")

    # Cleanup: Clear in-memory data (optional, for graceful shutdown)
    # In production with a database, you would close connections here
    await item_repository.clear()
    log.debug("Cleared item repository")

    log.info("Application shutdown complete")
