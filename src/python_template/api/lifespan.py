"""FastAPI lifespan context manager for startup/shutdown.

Initializes repositories and services, storing them in a typed AppState container.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from python_template.api.dependencies import AppState
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
        - Store in typed AppState container

    Shutdown:
        - Cleanup resources (database connections, etc.)

    The repository pattern allows easy swapping of storage backends:
        - Development: InMemoryRepository (dict-based)
        - Production: MongoRepository, PostgresRepository, etc.

    For ML applications, load models here:
        >>> model = load_model("model.pt")
        >>> predictor = PredictorService(model=model)
        >>> state = AppState(..., predictor=predictor)
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

    # Store in typed AppState container for dependency injection
    # This provides type safety throughout the application
    app.state.container = AppState(
        item_repository=item_repository,
        item_service=item_service,
    )

    log.info("Application initialized successfully")

    yield

    # Shutdown
    log.info("Application shutting down...")

    # Cleanup: Clear in-memory data (optional, for graceful shutdown)
    # In production with a database, you would close connections here
    await item_repository.clear()
    log.debug("Cleared item repository")

    log.info("Application shutdown complete")
