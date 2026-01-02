"""FastAPI lifespan context manager for startup/shutdown.

Initializes services and stores them in app.state for dependency injection.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from python_template.logging import configure_logging, get_logger
from python_template.services.items import ItemService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle.

    Startup:
        - Configure logging
        - Initialize services
        - Store services in app.state

    Shutdown:
        - Cleanup resources
    """
    # Configure logging first
    configure_logging()
    log = get_logger("python_template.startup")

    log.info("Application starting up...")

    # Initialize services
    item_service = ItemService()

    # Store in app.state for dependency injection
    app.state.item_service = item_service

    log.info("Application initialized successfully")

    yield

    # Shutdown
    log.info("Application shutting down...")

    # Add cleanup logic here if needed (e.g., close database connections)

    log.info("Application shutdown complete")
